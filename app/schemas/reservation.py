from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime


class ReservationBase(BaseModel):
    customer_name: str
    table_id: int
    reservation_time: datetime
    duration_minutes: int

    @field_validator("duration_minutes")
    def validate_duration(cls, value):
        if value <= 0:
            raise ValueError("Duration must be positive")
        return value

class ReservationCreate(ReservationBase):
    pass


class ReservationResponse(ReservationBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
