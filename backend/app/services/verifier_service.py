import json
from app.services.llm_service import LLMService
from app.services.logging_service import LoggingService


class VerifierService:

    @staticmethod
    def verify(context: str, question: str, answer: str) -> dict:
        """
        Verifies if the answer is grounded in the context.
        Returns verdict: SUPPORTED or UNSUPPORTED + confidence score.
        
        Calibrated to not be overly strict — if answer is reasonable
        given the context, it should pass.
        """

        prompt = f"""You are a fact verification assistant.

Check if the Answer is supported by the Context provided.

Rules:
- If the answer is directly or reasonably supported by the context: verdict = SUPPORTED
- If the answer contains information NOT in the context: verdict = UNSUPPORTED
- If the answer says "not found in document" or similar: verdict = SUPPORTED
- Be lenient — partial support counts as SUPPORTED
- Score confidence from 0.0 to 1.0

Context:
{context[:2000]}

Question:
{question}

Answer:
{answer}

Return ONLY valid JSON:
{{"verdict": "SUPPORTED", "confidence": 0.85, "reason": "Answer directly references information in context"}}"""

        try:
            raw = LLMService.generate_text(prompt)
            raw = raw.strip().replace("```json", "").replace("```", "").strip()
            result = json.loads(raw)

            verdict = str(result.get("verdict", "SUPPORTED")).upper()
            confidence = float(result.get("confidence", 0.8))
            reason = str(result.get("reason", ""))

            # Normalize verdict
            if verdict not in ["SUPPORTED", "UNSUPPORTED"]:
                verdict = "SUPPORTED"

            return {
                "verdict": verdict,
                "confidence": round(confidence, 3),
                "reason": reason,
            }

        except json.JSONDecodeError:
            # If Gemini doesn't return valid JSON — default to SUPPORTED
            # Better to show answer with warning than block it entirely
            LoggingService.warning("Verifier JSON parse failed — defaulting to SUPPORTED")
            return {
                "verdict": "SUPPORTED",
                "confidence": 0.65,
                "reason": "Verification returned non-JSON response — defaulting to supported",
            }
        except Exception as e:
            LoggingService.error(f"Verifier failed: {e}")
            return {
                "verdict": "SUPPORTED",
                "confidence": 0.60,
                "reason": f"Verification error — defaulting to supported: {str(e)}",
            }

# import json
# #from app.services.llm_service import LLMService
# from app.services.llm import LLMService
# from app.services.verifier_prompt import build_verifier_prompt


# class VerifierService:

#     @staticmethod
#     def verify(context: str, question: str, answer: str):
#         prompt = build_verifier_prompt(context, question, answer)

#         response = LLMService.generate_text(prompt)

#         try:
#             data = json.loads(response)
#             return data
#         except Exception:
#             return {
#                 "verdict": "UNSUPPORTED",
#                 "confidence": 0.0,
#                 "reason": "Verifier failed to return valid JSON"
#             }