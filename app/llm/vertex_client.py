def generate_response(prompt:str)->str:
    # ponytail: mock LLM call, always returns a canned response — swap for
    # a real Vertex AI call once GCP credentials are available
    return f"[mock LLM response] This is a placeholder answer for the prompt:\n\n{prompt}"