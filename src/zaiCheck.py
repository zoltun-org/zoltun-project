from zai import ZaiClient
from dotenv import load_dotenv
load_dotenv()


def check_model_availability(self):
try:
    # Standard OpenAI-compatible call to list models
    models = self.client.models.list()
    print("--- Available Models for your Key ---")
    for model in models.data:
        print(f"- {model.id}")
except Exception as e:
    print(f"Could not fetch models: {e}")

client = ZaiClient(api_key="ZAI_API_KEY")
check_model_availability(self)