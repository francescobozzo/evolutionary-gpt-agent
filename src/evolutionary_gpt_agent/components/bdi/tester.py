from typing import Any, Callable


class CodeTester:
    def __init__(
        self,
        code: str,
        function_name: str,
    ) -> None:
        self._code = code
        self._function_name = function_name
        self._callable_function: Callable[[], Any] | None = None

    def is_valid(self, **kwargs: Any) -> bool:
        try:
            exec(f"{self._code}")
            exec(f"self.{self._function_name} = {self._function_name}")
            self._callable_function = getattr(self, self._function_name)
            if not self._callable_function:
                raise
            self._callable_function(**kwargs)
        except Exception as e:
            print(
                f"Error testing code with function name {self._function_name}"
                f" and code \n\n{self._code}\n\n",
                e,
                flush=True,
            )
            return False

        return True

    def __call__(self, **kwargs: Any) -> Any:
        if not self._callable_function:
            raise
        return self._callable_function(**kwargs)
