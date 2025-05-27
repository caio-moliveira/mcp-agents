from pydantic import BaseModel, Field
from datetime import date
from typing import List


class TravelInput(BaseModel):
    """Structured travel planning input schema"""

    departure: str = Field(..., description="City or airport of departure")
    destination: str = Field(..., description="Destination city")
    start_date: date = Field(..., description="Departure date")
    end_date: date = Field(..., description="Return date")
    num_travelers: int = Field(..., description="Number of travelers")
    attractions: List[str] = Field(
        ..., description="Desired attractions like 'cultural', 'pubs', 'parks'"
    )
    accommodation_type: str = Field(
        ..., description="Preferred accommodation type (e.g., hotel, apartment)"
    )
