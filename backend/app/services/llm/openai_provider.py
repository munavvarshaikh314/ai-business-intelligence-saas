from fastapi import HTTPException
from openai import APIConnectionError, AuthenticationError, OpenAI, RateLimitError

from app.config import settings
from app.services.llm.base import BaseLLMProvider
from app.services.logging_service import LoggingService


class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY missing")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    def _handle_error(self, err: Exception):
        if isinstance(err, RateLimitError):
            err_str = str(err).lower()
            if "insufficient_funds" in err_str or "quota" in err_str or "billing" in err_str:
                LoggingService.error(f"OpenAI quota exhausted: {err}")
                raise HTTPException(status_code=402, detail="OpenAI quota exhausted.")
            raise HTTPException(status_code=429, detail="OpenAI rate limit reached.")

        if isinstance(err, AuthenticationError):
            LoggingService.error(f"OpenAI auth error: {err}")
            raise HTTPException(status_code=500, detail="OpenAI configuration error.")

        if isinstance(err, APIConnectionError):
            LoggingService.error(f"OpenAI connection error: {err}")
            raise HTTPException(status_code=503, detail="OpenAI service unavailable.")

        LoggingService.error(f"OpenAI unexpected error: {err}")
        raise HTTPException(status_code=500, detail="OpenAI service error.")

    def _chat(self, prompt: str, system: str, temperature: float = 0.0):
        return self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )

    def generate_text(self, prompt: str) -> str:
        try:
            response = self._chat(prompt, "You are a helpful AI assistant.")
            return response.choices[0].message.content.strip()
        except HTTPException:
            raise
        except Exception as err:
            self._handle_error(err)

    def generate_text_with_usage(self, prompt: str):
        try:
            response = self._chat(prompt, "You are a helpful AI assistant.")
            usage = response.usage
            return {
                "text": response.choices[0].message.content.strip(),
                "prompt_tokens": usage.prompt_tokens if usage else 0,
                "completion_tokens": usage.completion_tokens if usage else 0,
            }
        except HTTPException:
            raise
        except Exception as err:
            self._handle_error(err)

    def generate_sql(self, prompt: str) -> str:
        try:
            response = self._chat(prompt, "You are an expert SQL generator for PostgreSQL.")
            return response.choices[0].message.content.strip()
        except HTTPException:
            raise
        except Exception as err:
            self._handle_error(err)

    def stream_text(self, prompt: str):
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except HTTPException:
            raise
        except Exception as err:
            self._handle_error(err)
