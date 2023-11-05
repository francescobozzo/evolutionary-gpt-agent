import openai


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
        openai.api_key = api_key
        openai.api_base = api_base
        openai.api_type = api_type
        openai.api_version = openai.api_version
        self._deployment = deployment
        self._model = model

    def ask(
        self,
        prompt: str,
    ) -> str:
        chat_completion = openai.ChatCompletion.create(
            engine=self._deployment,
            model=self._model,
            messages=[
                {
                    "role": self.role,
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
