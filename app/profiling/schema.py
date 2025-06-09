from pydantic import BaseModel
from typing import Optional

class UserProfile(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    activity_level: Optional[str] = None  # Expected: Sedentary, Moderate, Active
    dietary_preference: Optional[str] = None  # Expected: Vegan, Non-Vegan, etc
    sleep_quality: Optional[str] = None  # Expected: Poor, Average, Good
    stress_level: Optional[str] = None  # Expected: Low, Medium, High
    health_goals: Optional[str] = None
