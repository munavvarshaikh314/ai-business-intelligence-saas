from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        raise NotImplementedError

    def generate_text_with_usage(self, prompt: str):
        return {
            "text": self.generate_text(prompt),
            "prompt_tokens": 0,
            "completion_tokens": 0,
        }

    def generate_sql(self, prompt: str) -> str:
        return self.generate_text(prompt)

    def stream_text(self, prompt: str):
        yield self.generate_text(prompt)

    def classify_intent(self, prompt: str):
        return self.generate_text(prompt)

    def summarize(self, text: str, max_words: int = 150):
        prompt = f"Summarize the following text in {max_words} words or fewer:\n\n{text}"
        return self.generate_text(prompt)
