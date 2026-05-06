import re


def clean_text(text: str) -> str:
    if not text:
        return ""

    # remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    # remove weird characters but keep punctuation
    text = re.sub(r"[^\w\s\.\,\:\;\-\(\)\[\]\{\}\?\!\/]", "", text)

    return text.strip()