from openai import OpenAI

from common import constants as CONSTS
from common import prompts as PROMPTS

openai_client = OpenAI(api_key=CONSTS.OPENAI_API_KEY)

def generate_followup_question(question: str = "", user_input: str = "", remaining_fields: list[str] | None = None) -> str:
    try:
        field_list = "\n".join(f"- {field}" for field in remaining_fields) if remaining_fields else "None"

        dynamic_prompt = PROMPTS.FOLLOWUP_QUESTION_PROMPT_TEMPLATE.format(
            question=question,
            user_input=user_input,
            field_list=field_list
        )

        completion = openai_client.chat.completions.create(
            model=CONSTS.OPENAI_MODEL,
            messages=[{"role": "user", "content": dynamic_prompt}]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"LLM question generation failed: {e}")