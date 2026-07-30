"""Constants for memory and vector storage configuration."""

DEFAULT_COLLECTION_NAME = "memories"

# Vector sizes for different embedding models
VECTOR_SIZES = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
}

DEFAULT_VECTOR_SIZE = 3072  # Default to text-embedding-3-large

DEFAULT_DISTANCE = "COSINE"


def get_vector_size_for_model(model: str) -> int:
    """Get the vector size for a specific embedding model.

    Args:
        model: The name of the embedding model.

    Returns:
        The vector dimension size for the model, or DEFAULT_VECTOR_SIZE if not found.
    """
    return VECTOR_SIZES.get(model, DEFAULT_VECTOR_SIZE)
