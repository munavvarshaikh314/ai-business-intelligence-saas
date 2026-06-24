import json
from openai import OpenAI
from app.config import settings
from app.services.llm.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):

    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY missing")

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    def generate_text(self, prompt: str) -> str:
        res = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        return res.choices[0].message.content.strip()

    def generate_json(self, prompt: str) -> dict:
        text = self.generate_text(prompt)

        try:
            return json.loads(text)
        except Exception:
            return {"raw": text}