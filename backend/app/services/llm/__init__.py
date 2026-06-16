from app.services.llm.factory import get_llm_provider

_provider = None


def _get_provider():
    global _provider
    if _provider is None:
        _provider = get_llm_provider()
    return _provider


class LLMService:
    @staticmethod
    def generate_text_with_usage(prompt: str):
        return _get_provider().generate_text_with_usage(prompt)

    @staticmethod
    def generate_text(prompt: str):
        return _get_provider().generate_text(prompt)

    @staticmethod
    def generate_sql(prompt: str):
        return _get_provider().generate_sql(prompt)

    @staticmethod
    def stream_text(prompt: str):
        return _get_provider().stream_text(prompt)

    @staticmethod
    def classify_intent(prompt: str):
        return _get_provider().classify_intent(prompt)

    @staticmethod
    def summarize(text: str, max_words: int = 150):
        return _get_provider().summarize(text, max_words)
