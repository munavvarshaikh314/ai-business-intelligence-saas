import json
from app.services.llm_service import LLMService
from app.services.verifier_prompt import build_verifier_prompt


class VerifierService:

    @staticmethod
    def verify(context: str, question: str, answer: str):
        prompt = build_verifier_prompt(context, question, answer)

        response = LLMService.generate_text(prompt)

        try:
            data = json.loads(response)
            return data
        except Exception:
            return {
                "verdict": "UNSUPPORTED",
                "confidence": 0.0,
                "reason": "Verifier failed to return valid JSON"
            }