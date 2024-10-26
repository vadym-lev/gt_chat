from pydantic import BaseModel, validator
from typing import Literal


class TextPayload(BaseModel):
    type: Literal["chat_item", "summary", "article"]
    text: str

    @validator("text")
    def validate_text_length(cls, v, values):
        text_type = values.get("type")
        if text_type == "chat_item" and len(v) > 300:
            raise ValueError("Chat item text exceeds 300 characters.")
        elif text_type == "summary" and len(v) > 3000:
            raise ValueError("Summary text exceeds 3000 characters.")
        elif text_type == "article" and len(v) < 300000:
            raise ValueError("Article text is less than 300000 characters.")
        return v
