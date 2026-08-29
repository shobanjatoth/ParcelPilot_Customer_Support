import os
from openai import OpenAI
from app.config import get_settings

settings = get_settings()
groq_api_key = settings.groq_api_key or os.getenv("GROQ_API_KEY")

client = OpenAI(
    api_key=groq_api_key,
    base_url="https://api.groq.com/openai/v1",
)

models = client.models.list()
for model in models:
    print(model.id)