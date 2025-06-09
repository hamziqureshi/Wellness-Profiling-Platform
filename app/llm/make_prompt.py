from openai import OpenAI
from typing import Optional

from common import constants as CONSTS
from common import prompts as PROMPTS

# Initialize your OpenAI client
openai_client = OpenAI(api_key=CONSTS.OPENAI_API_KEY)

def build_user_profile_extraction_prompt(field: str, question: str, user_text: str) -> str:
    if field not in CONSTS.FIELD_METADATA:
        raise ValueError(f"Unsupported field: {field}")
    field_label = CONSTS.FIELD_METADATA[field]
    
    return PROMPTS.EXTRACTION_PROMPT_TEMPLATE.format(
        field_label=field_label,
        question=question,
        user_text=user_text
    )


def extract_user_profile_field(field: str, question: str, user_text: str) -> str:
    try:
        prompt = build_user_profile_extraction_prompt(field, question, user_text)
        completion = openai_client.chat.completions.create(
            model=CONSTS.OPENAI_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"LLM extraction failed: {e}")
