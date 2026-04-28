from openai import OpenAI, AsyncOpenAI


def connect_to_minimax(api_key):
   return OpenAI(base_url='https://api.minimax.io/v1',api_key=api_key)
    