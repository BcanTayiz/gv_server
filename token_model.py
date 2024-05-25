from pydantic import BaseModel, Field

class Token(BaseModel):
    token: str = Field(..., pattern=r"^USER\d{3}$")
