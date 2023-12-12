import json
from typing import Any

import instructor
import openai
import tiktoken
from pydantic import BaseModel

from models.db.models import Event, Experiment, Perceiver, PromptTemplate


def _load_prompt(prompt: str, prefix: str) -> str:
    with open(prompt, "r") as f:
        template = f.read()

    return prefix + "\n" + template


_PROMPT_DIR = "/prompts"

_NEW_PERCEIVER_PROMPT_PATH = f"{_PROMPT_DIR}/new_perceiver.template"
_REFACTOR_PERCEIVER_PROMPT_PATH = f"{_PROMPT_DIR}/refactor_perceiver.template"
_NEW_GOAL_PROMPT_PATH = f"{_PROMPT_DIR}/single_goal.template"
_EXPAND_NEW_GOAL_PROMPT_PATH = f"{_PROMPT_DIR}/expand_single_goal.template"
_BELIEF_SET_PROMPT_PATH = f"{_PROMPT_DIR}/belief_set_representation.template"


def load_prompt_templates(
    experiment: Experiment, prompt_prefix: str
) -> dict[str, PromptTemplate]:
    _NEW_PERCEIVER_PROMPT = _load_prompt(_NEW_PERCEIVER_PROMPT_PATH, prompt_prefix)
    _REFACTOR_PERCEIVER_PROMPT = _load_prompt(
        _REFACTOR_PERCEIVER_PROMPT_PATH, prompt_prefix
    )
    _NEW_GOAL_PROMPT = _load_prompt(_NEW_GOAL_PROMPT_PATH, prompt_prefix)
    _EXPAND_NEW_GOAL_PROMPT = _load_prompt(_EXPAND_NEW_GOAL_PROMPT_PATH, prompt_prefix)

    return {
        "new_perceiver": PromptTemplate(
            experiment=experiment,
            template_type="new_perceiver",
            template=_NEW_PERCEIVER_PROMPT,
        ),
        "new_goal": PromptTemplate(
            experiment=experiment,
            template_type="new_goal",
            template=_NEW_GOAL_PROMPT,
        ),
        "expand_goal": PromptTemplate(
            experiment=experiment,
            template_type="expand_goal",
            template=_EXPAND_NEW_GOAL_PROMPT,
        ),
        "refactor_perceiver": PromptTemplate(
            experiment=experiment,
            template_type="refactor_perceiver",
            template=_REFACTOR_PERCEIVER_PROMPT,
        ),
    }


class Conversation:
    def __init__(self) -> None:
        self._user_messages: list[str] = []
        self._gpt_messages: list[str] = []
        self._conversation: list[dict[str, str]] = []
        self._number_of_tokens = 0
        self._last_tokens = 0

    def add(self, prompt: str, answer: str) -> None:
        self._user_messages.append(prompt)
        self._gpt_messages.append(answer)
        self._conversation.append(
            {"role": "user", "content": prompt},
        )
        self._conversation.append(
            {"role": "assistant", "content": answer},
        )
        self._last_tokens = len(prompt) + len(answer)
        self._number_of_tokens += self._last_tokens

    def invalidate_last_exchange(self) -> None:
        if self._user_messages:
            self._user_messages.pop()
        if self._user_messages:
            self._user_messages.pop()
        if self._conversation:
            self._conversation.pop()
        self._number_of_tokens -= self._last_tokens
        if self._number_of_tokens < 0:
            self._number_of_tokens = 0

    def get_conversation(self) -> list[dict[str, str]]:
        return self._conversation

    def number_of_tokens(self) -> int:
        return self._number_of_tokens


class _Perceiver(BaseModel):
    python_code: str
    description: str | None


class _Plan(BaseModel):
    python_code: str
    description: str | None


class _Goal(BaseModel):
    text: str


class _BeliefSetRepresenation(BaseModel):
    python_code: str
    description: str | None


class Client:
    def __init__(
        self,
        api_key: str,
        api_base: str,
        api_type: str,
        api_version: str,
        deployment: str,
        model: str,
        prompt_prefix: str,
    ) -> None:
        self._deployment = deployment
        self._model = deployment
        if api_type == "azure":
            self._model = deployment
            self._client = instructor.patch(
                openai.AzureOpenAI(
                    api_key=api_key,
                    api_version=api_version,
                    azure_endpoint=api_base,
                )
            )
        else:
            raise NotImplementedError(f"gpt client: {api_type} not implemented")
        self._role = "user"

        self._new_perceiver_prompt = _load_prompt(
            _NEW_PERCEIVER_PROMPT_PATH, prompt_prefix
        )
        self._refactor_perceiver_prompt = _load_prompt(
            _REFACTOR_PERCEIVER_PROMPT_PATH, prompt_prefix
        )
        self._new_goal_prompt = _load_prompt(_NEW_GOAL_PROMPT_PATH, prompt_prefix)
        self._expand_new_goal_prompt = _load_prompt(
            _EXPAND_NEW_GOAL_PROMPT_PATH, prompt_prefix
        )
        self._belief_set_representation = _load_prompt(_BELIEF_SET_PROMPT_PATH, "")

    def ask_perceiver(
        self, function_name: str, belief_set: dict[Any, Any], events: str
    ) -> tuple[str, str]:
        prompt = self._new_perceiver_prompt.format(
            events,
            json.dumps(belief_set, indent=2),
            function_name,
        )
        perceiver = self._client.chat.completions.create(
            model=self._model,
            response_model=_Perceiver,
            max_retries=5,
            messages=[
                {
                    "role": self._role,
                    "content": prompt,
                }
            ],
        )

        return prompt, perceiver.python_code

    def ask_plan(
        self, function_name: str, belief_set: dict[Any, Any]
    ) -> tuple[str, str]:
        prompt = self._new_goal_prompt.format(json.dumps(belief_set))

        goal = self._client.chat.completions.create(
            model=self._model,
            max_retries=5,
            response_model=_Goal,
            messages=[{"role": self._role, "content": prompt}],
        )

        prompt = self._expand_new_goal_prompt.format(
            json.dumps(belief_set), goal, function_name
        )
        plan = self._client.chat.completions.create(
            model=self._model,
            response_model=_Plan,
            max_retries=10,
            messages=[
                {
                    "role": self._role,
                    "content": prompt,
                }
            ],
        )

        return prompt, plan.python_code

    def ask(
        self,
        prompt: str,
    ) -> str:
        chat_completion = openai.ChatCompletion.create(
            engine=self._deployment,
            model=self._model,
            messages=[
                {
                    "role": self._role,
                    "content": prompt,
                }
            ],
        )

        if not isinstance(chat_completion.choices[0].message.content, str):
            raise Exception("gpt client didn't return a str")

        return chat_completion.choices[0].message.content

    def refactor_perceivers(
        self,
        events_by_perceivers: dict[Perceiver, list[Event]],
        function_name: str,
    ) -> tuple[str, str]:
        events_prompt_content = ""
        perceivers_prompt_content = ""

        encoder = tiktoken.encoding_for_model("gpt-4")

        for perceiver, events in events_by_perceivers.items():
            event_current_content = "\n".join(
                [json.dumps(e.data, separators=(",", ":")) for e in events]
            )
            perceiver_current_content = perceiver.code

            if (
                len(
                    encoder.encode(
                        f"{events_prompt_content}\n{event_current_content}"
                        f"\n{perceivers_prompt_content}\n{perceiver_current_content}"
                    )
                )
                > 8000
            ):
                break

            events_prompt_content += "\n" + event_current_content
            perceivers_prompt_content += "\n" + perceiver_current_content

        prompt = self._refactor_perceiver_prompt.format(
            events_prompt_content,
            perceivers_prompt_content,
            function_name,
        )

        perceiver = self._client.chat.completions.create(
            model=self._model,
            response_model=_Perceiver,
            max_retries=5,
            messages=[{"role": self._role, "content": prompt}],
        )

        return prompt, perceiver.python_code

    def ask_belief_set_represenation_generator(
        self, function_name: str, belief_set: dict[Any, Any]
    ) -> str:
        prompt = self._belief_set_representation.format(
            function_name, json.dumps(belief_set)
        )

        representationGenerator = self._client.chat.completions.create(
            model=self._model,
            response_model=_BeliefSetRepresenation,
            max_retries=5,
            messages=[{"role": self._role, "content": prompt}],
        )

        return representationGenerator.python_code

    # def ask_discussion(
    #     self,
    #     prompt: str,
    # ) -> str:
    #     messages = self.conversation.get_conversation() + [
    #         {
    #             "role": self.role,
    #             "content": prompt,
    #         }
    #     ]
    #     chat_completion = openai.ChatCompletion.create(
    #         engine=self._deployment,
    #         model=self._model,
    #         messages=messages,
    #     )

    #     answer = chat_completion.choices[0].message.content
    #     self.conversation.add(prompt, answer)

    #     return answer

    # def invalidate_last_exchange(self):
    #     self.conversation.invalidate_last_exchange()
