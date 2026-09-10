from pydantic import BaseModel, ConfigDict, Field


class ModelConfig(BaseModel):
    """
    Configuration for an open-weight image generation model.
    """

    model_config = ConfigDict(extra="forbid")

    model_id: str = Field(
        default="stabilityai/stable-diffusion-xl-base-1.0"
    )

    torch_dtype: str = "float16"

    device: str = "auto"

    enable_cpu_offload: bool = True

    enable_attention_slicing: bool = True