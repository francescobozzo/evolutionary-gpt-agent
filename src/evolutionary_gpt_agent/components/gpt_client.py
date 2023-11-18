import json

import instructor
import openai
from pydantic import BaseModel

from models.db.models import Experiment, PromptTemplate


def _load_prompt(prompt: str, prefix: str | None) -> str:
    if prefix:
        with open(prefix, "r") as f:
            prefix = f.read()
    else:
        prefix = ""

    with open(prompt, "r") as f:
        template = f.read()

    return prefix + "\n" + template


_PROMPT_DIR = "/prompts"

_PREFIX_PROMPT_PATH = f"{_PROMPT_DIR}/deliveroo_prefix.template"
_NEW_PERCEIVER_PROMPT_PATH = f"{_PROMPT_DIR}/new_perceiver.template"
_NEW_GOAL_PROMPT_PATH = f"{_PROMPT_DIR}/single_goal.template"
_EXPAND_NEW_GOAL_PROMPT_PATH = f"{_PROMPT_DIR}/expand_single_goal.template"
_NEW_PERCEIVER_PROMPT = _load_prompt(_NEW_PERCEIVER_PROMPT_PATH, _PREFIX_PROMPT_PATH)
_NEW_GOAL_PROMPT = _load_prompt(_NEW_GOAL_PROMPT_PATH, _PREFIX_PROMPT_PATH)
_EXPAND_NEW_GOAL_PROMPT = _load_prompt(
    _EXPAND_NEW_GOAL_PROMPT_PATH, _PREFIX_PROMPT_PATH
)


def load_prompt_templates(experiment: Experiment) -> dict[str, PromptTemplate]:
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
    }


class Conversation:
    def __init__(self):
        self._user_messages = []
        self._gpt_messages = []
        self._conversation = []
        self._number_of_tokens = 0
        self._last_tokens = 0

    def add(self, prompt, answer):
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

    def invalidate_last_exchange(self):
        if self._user_messages:
            self._user_messages.pop()
        if self._user_messages:
            self._user_messages.pop()
        if self._conversation:
            self._conversation.pop()
        self._number_of_tokens -= self._last_tokens
        if self._number_of_tokens < 0:
            self._number_of_tokens = 0

    def get_conversation(self):
        return self._conversation

    def number_of_tokens(self):
        return self._number_of_tokens


class _Perceiver(BaseModel):
    python_code: str
    description: str | None


class _Plan(BaseModel):
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

    def ask_perceiver(
        self, function_name: str, belief_set: dict, events: str
    ) -> tuple[str, str]:
        prompt = _NEW_PERCEIVER_PROMPT.format(
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

    def ask_plan(self, function_name: str, belief_set: dict) -> str:
        prompt = _NEW_GOAL_PROMPT.format(json.dumps(belief_set))

        goal = self._client.chat.completions.create(
            model=self._model, messages=[{"role": self._role, "content": prompt}]
        )

        prompt = _EXPAND_NEW_GOAL_PROMPT.format(
            json.dumps(belief_set), goal, function_name
        )
        plan = self._client.chat.completions.create(
            model=self._model,
            response_model=_Plan,
            max_retries=5,
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

        return chat_completion.choices[0].message.content

    def ask_discussion(
        self,
        prompt: str,
    ) -> str:
        messages = self.conversation.get_conversation() + [
            {
                "role": self.role,
                "content": prompt,
            }
        ]
        chat_completion = openai.ChatCompletion.create(
            engine=self._deployment,
            model=self._model,
            messages=messages,
        )

        answer = chat_completion.choices[0].message.content
        self.conversation.add(prompt, answer)

        return answer

    def invalidate_last_exchange(self):
        self.conversation.invalidate_last_exchange()
