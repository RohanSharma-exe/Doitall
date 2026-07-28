from pydantic import BaseModel


class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    input_cost: float = 0.0
    output_cost: float = 0.0
    total_cost: float = 0.0
