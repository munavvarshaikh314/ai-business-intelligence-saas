import re

BLOCK_PATTERNS = [
    r"ignore previous instructions",
    r"bypass security",
    r"reveal system prompt",
    r"show hidden prompt",
    r"developer mode",
    r"act as",
    r"you are now",
    r"disable safety",
    r"jailbreak",
    r"do anything now",
    r"override"
]


class PromptInjectionGuard:

    @staticmethod
    def is_malicious(query: str) -> bool:
        q = query.lower().strip()

        for pattern in BLOCK_PATTERNS:
            if re.search(pattern, q):
                return True

        return False

    @staticmethod
    def sanitize(query: str) -> str:
        # remove weird characters (basic sanitation)
        query = query.replace("\x00", "")
        query = query.strip()
        return query