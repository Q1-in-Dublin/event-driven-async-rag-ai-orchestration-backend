import vertexai
from vertexai.generative_models import GenerativeModel
import os

# def generate_response(prompt: str) -> str:
#     vertexai.init()
#     model = GenerativeModel("gemini-1.5-flash")
#     response = model.generate_content(prompt)
#     return response.text

def generate_response(prompt: str) -> str:
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    vertexai.init(project=project_id, location="global")
    model = GenerativeModel("gemini-3.5-flash")
    response = model.generate_content(prompt)
    return response.text