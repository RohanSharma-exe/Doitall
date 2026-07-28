from doitall.models.model_info import ModelInfo


def test_model_info_defaults():
    model = ModelInfo(
        provider="gemini",
        id="gemini-2.5-flash",
        name="Gemini 2.5 Flash",
    )

    assert model.provider == "gemini"
    assert model.id == "gemini-2.5-flash"
    assert model.name == "Gemini 2.5 Flash"

    assert model.supports_chat is True
    assert model.supports_streaming is False
    assert model.supports_embeddings is False
    assert model.supports_vision is False
    assert model.supports_image_generation is False
    assert model.supports_audio is False
    assert model.supports_tool_calling is False


def test_model_info_capabilities():
    model = ModelInfo(
        provider="groq",
        id="llama-3.3-70b-versatile",
        name="Llama 3.3 70B",
        context_window=131072,
        max_output_tokens=8192,
        supports_streaming=True,
        supports_tool_calling=True,
    )

    assert model.context_window == 131072
    assert model.max_output_tokens == 8192
    assert model.supports_streaming is True
    assert model.supports_tool_calling is True
