import json
from app.services.llm_service import LLMService
from app.services.conflict_prompt import build_conflict_prompt


class ConflictDetectionService:

    @staticmethod
    def detect(context: str):
        prompt = build_conflict_prompt(context)

        response = LLMService.generate_text(prompt)

        try:
            data = json.loads(response)
            return data
        except Exception:
            return {
                "conflict": False,
                "conflicting_points": []
            }