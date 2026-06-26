import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# உன் account-ல available models பாரு
for model in genai.list_models():
    print(model.name)