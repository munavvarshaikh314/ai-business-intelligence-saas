from openai import OpenAI
from app.config import settings
from typing import Generator

class LLMService:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    @staticmethod
    def generate_text_with_usage(prompt: str):
        response = LLMService.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )

        text = response.choices[0].message.content.strip()

        usage = response.usage
        prompt_tokens = usage.prompt_tokens if usage else 0
        completion_tokens = usage.completion_tokens if usage else 0

        return {
            "text": text,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens
        }
    
    @staticmethod
    def stream_text(prompt: str):
        stream = LLMService.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            stream=True
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    @staticmethod
    def generate_sql(prompt: str) -> str:
        response = LLMService.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert SQL generator for PostgreSQL."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )

        return response.choices[0].message.content.strip()