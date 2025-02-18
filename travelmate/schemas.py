from pydantic import BaseModel
from typing import Optional, List

class TripPlannerInput(BaseModel):
    origin: str
    cities: str
    date_range: str 
    interests: str

class InputSchema(BaseModel):
    tool_name: str = "plan_trip"
    tool_input_data: TripPlannerInput