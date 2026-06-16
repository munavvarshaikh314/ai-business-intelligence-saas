import json
from fastapi import HTTPException
from google.api_core.exceptions import GoogleAPIError, NotFound, ResourceExhausted, Unauthenticated
import google.generativeai as genai
from app.config import settings
from app.services.llm.base import BaseLLMProvider
from app.services.logging_service import LoggingService


class GeminiProvider(BaseLLMProvider):

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY missing")

        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    def _handle_error(self, err: Exception):
        if isinstance(err, NotFound) or "not found" in str(err).lower():
            LoggingService.error(f"Gemini model not found: {err}")
            raise HTTPException(
                status_code=500,
                detail=f"Gemini model '{settings.GEMINI_MODEL}' is not available for this API key. Use gemini-2.0-flash or gemini-2.5-flash.",
            )

        if isinstance(err, ResourceExhausted):
            LoggingService.error(f"Gemini quota/rate limit reached: {err}")
            raise HTTPException(
                status_code=429,
                detail="Gemini quota or rate limit reached. Please wait or check your Gemini billing/quota.",
            )

        if isinstance(err, Unauthenticated):
            LoggingService.error(f"Gemini auth error: {err}")
            raise HTTPException(
                status_code=500,
                detail="Gemini configuration error. Check GEMINI_API_KEY.",
            )

        if isinstance(err, GoogleAPIError):
            LoggingService.error(f"Gemini API error: {err}")
            raise HTTPException(
                status_code=503,
                detail="Gemini service is temporarily unavailable.",
            )

        LoggingService.error(f"Gemini unexpected error: {err}")
        raise HTTPException(status_code=500, detail="Gemini service error.")

    @staticmethod
    def _extract_text(response) -> str:
        text = getattr(response, "text", None)
        if text:
            return text.strip()
        candidates = getattr(response, "candidates", None) or []
        if candidates:
            parts = getattr(candidates[0].content, "parts", []) or []
            return "".join(getattr(part, "text", "") for part in parts).strip()
        return ""

    def generate_text(self, prompt: str) -> str:
        try:
            res = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.0,
                    max_output_tokens=2048,
                ),
            )
            text = self._extract_text(res)
            if not text:
                raise HTTPException(status_code=502, detail="Gemini returned an empty response.")
            return text
        except HTTPException:
            raise
        except Exception as err:
            self._handle_error(err)

    def generate_text_with_usage(self, prompt: str):
        return {
            "text": self.generate_text(prompt),
            "prompt_tokens": 0,
            "completion_tokens": 0,
        }

    def generate_sql(self, prompt: str) -> str:
        sql_prompt = (
            "You are an expert PostgreSQL SQL generator. "
            "Return only the SQL query, no markdown fences, no explanation.\n\n"
            f"{prompt}"
        )
        return self.generate_text(sql_prompt).replace("```sql", "").replace("```", "").strip()

    def stream_text(self, prompt: str):
        try:
            stream = self.model.generate_content(prompt, stream=True)
            for chunk in stream:
                text = self._extract_text(chunk)
                if text:
                    yield text
        except HTTPException:
            raise
        except Exception as err:
            self._handle_error(err)

    def generate_json(self, prompt: str) -> dict:
        text = self.generate_text(prompt)

        try:
            return json.loads(text)
        except Exception:
            return {"raw": text}
