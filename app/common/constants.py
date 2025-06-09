import os
import dotenv
from pathlib import Path

env_file_path = os.path.join(str(Path.home()), '.env')

if os.path.exists(env_file_path):
    dotenv.load_dotenv(env_file_path)
else:
    dotenv.load_dotenv()

SUCCESS = 1
FAILURE = 0

IS_DEV = bool(os.getenv('IS_DEV', '0') == '1')
PORT = int(os.getenv('FAST_API_PORT'))
HOST = os.getenv('HOST')


OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = "gpt-4o-mini"

MAX_QUESTIONS = 5

FIELD_METADATA = {
    "age": "Age",
    "gender": "Gender",
    "activity_level": "Daily activity level (Sedentary, Moderate, Active)",
    "dietary_preference": "Dietary preferences (Vegan, Non-Vegan, etc)",
    "sleep_quality": "Sleep quality (Poor, Average, Good)",
    "stress_level": "Stress level (Low, Medium, High)",
    "health_goals": "Health goals"
}