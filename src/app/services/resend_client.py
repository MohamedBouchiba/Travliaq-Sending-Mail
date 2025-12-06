import requests
from app.core.config import get_settings


class ResendClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.endpoint = "https://api.resend.com/emails"

    def send_email(self, to: str, subject: str, html_body: str, text_body: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.settings.resend_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "from": self.settings.email_from,
            "to": [to],
            "subject": subject,
            "html": html_body,
            "text": text_body,
        }
        response = requests.post(self.endpoint, json=payload, headers=headers, timeout=30)
        if response.status_code not in (200, 202):
            raise RuntimeError(f"Resend request failed: {response.text}")
        data = response.json()
        return data.get("id", "")
