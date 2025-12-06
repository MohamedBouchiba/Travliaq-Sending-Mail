import json
import requests
from app.core.config import get_settings


class LLMClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.endpoint = "https://openrouter.ai/api/v1/chat/completions"

    def generate_email_content(self, messages: list[dict]) -> dict:
        payload = {
            "model": self.settings.llm_model_name,
            "messages": messages,
            "reasoning": {"enabled": True},
        }
        headers = {
            "Authorization": f"Bearer {self.settings.llm_api_key}",
            "Content-Type": "application/json",
        }
        response = requests.post(self.endpoint, data=json.dumps(payload), headers=headers, timeout=60)
        if response.status_code != 200:
            raise RuntimeError(f"LLM request failed: {response.text}")
        body = response.json()
        if "choices" not in body or not body["choices"]:
            raise RuntimeError("LLM response missing choices")
        message = body["choices"][0].get("message", {})
        content = message.get("content")
        if not content:
            raise RuntimeError("LLM response missing content")
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError("LLM returned non-JSON content") from exc
