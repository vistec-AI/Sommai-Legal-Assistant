from core.embeddings.custom_embedding.model import InstructorEmbeddings

def get_instructor_embedding_model(model_name: str):
    return InstructorEmbeddings(model_name=model_name)