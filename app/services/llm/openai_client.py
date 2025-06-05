import openai
from app.infrastructure.config import get_settings

class OpenAIClient:
    def __init__(self):
        self.api_key = get_settings().openai_api_key
        openai.api_key = self.api_key

    async def extract_json(self, prompt: str, temperature: float = 0.3, model: str = "gpt-4o") -> str:
        response = await openai.ChatCompletion.acreate(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return response.choices[0].message.content