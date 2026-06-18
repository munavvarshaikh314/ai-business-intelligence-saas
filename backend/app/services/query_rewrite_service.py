from app.services.llm import LLMService # Make sure this points to your retry-enabled LLMService
from app.services.query_rewrite_prompt import build_rewrite_prompt
from app.services.logging_service import LoggingService
class QueryRewriteService:

    @staticmethod
    def rewrite(chat_history: str, question: str) -> str:
        prompt = build_rewrite_prompt(chat_history, question)
        
        try:
            # If you want to use the retry logic we built earlier, use generate_text_with_usage
            # result = LLMService.generate_text_with_usage(prompt)
            # rewritten = result["text"].replace('"', '').strip()
            
            # Or stick to your current generate_text:
            rewritten = LLMService.generate_text(prompt)
            rewritten = rewritten.replace('"', '').strip()

            if not rewritten:
                return question
                
            # 🔥 Add these prints so you can see the magic happen in your terminal!
            LoggingService.debug(f"🔍 [DEBUG] Original Query: '{question}'")
            LoggingService.debug(f"✨ [DEBUG] Rewritten Query: '{rewritten}'")

            return rewritten
            
        except Exception as e:
            # If the AI fails (like a rate limit), just use the original question instead of crashing!
            LoggingService.warning(f"⚠️ [WARNING] Query Rewrite Failed: {e}. Falling back to original question.")
            return question


# #from app.services.llm_service import LLMService
# from app.services.llm import LLMService
# from app.services.query_rewrite_prompt import build_rewrite_prompt


# class QueryRewriteService:

#     @staticmethod
#     def rewrite(chat_history: str, question: str) -> str:
#         prompt = build_rewrite_prompt(chat_history, question)
#         rewritten = LLMService.generate_text(prompt)

#         rewritten = rewritten.replace('"', '').strip()

#         # If LLM returns empty, fallback
#         if not rewritten:
#             return question

#         return rewritten