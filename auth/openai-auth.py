import os
import openai

def get_openai_client():
    """
    Return the authenticated OpenAI client.
    """
    api_key = os.environ['OPENAI_API_KEY']
    client = openai.OpenAI(api_key=api_key)
    return client