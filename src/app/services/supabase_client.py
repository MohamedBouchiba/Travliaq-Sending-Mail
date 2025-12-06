from typing import Optional
from uuid import UUID
import requests
from pydantic import BaseModel, HttpUrl
from app.core.config import get_settings


class TripSummary(BaseModel):
    id: UUID
    questionnaire_id: UUID
    run_id: Optional[str]
    user_email: str
    persona: Optional[str]
    summary_paragraph: Optional[str]
    destination: str
    destination_en: Optional[str]
    country_code: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    total_days: Optional[int]
    total_nights: Optional[int]
    travelers_count: Optional[int]
    travel_style: Optional[str]
    rhythm: Optional[str]
    total_price: Optional[float]
    price_flights: Optional[float]
    price_hotels: Optional[float]
    price_activities: Optional[float]
    budget_currency: Optional[str]
    flight_from: Optional[str]
    flight_to: Optional[str]
    flight_duration: Optional[str]
    hotel_name: Optional[str]
    hotel_rating: Optional[float]
    average_weather: Optional[str]
    main_image_url: Optional[HttpUrl]
    gallery_urls: Optional[list[str]]
    steps_count: Optional[int]
    activities_summary: Optional[list[str]]
    pipeline_status: Optional[str]
    generated_at: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


class SupabaseClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = f"{self.settings.supabase_url}"
        self.headers = {
            "apikey": self.settings.supabase_service_key,
            "Authorization": f"Bearer {self.settings.supabase_service_key}",
        }

    def fetch_trip_summary(self, summary_id: UUID) -> Optional[TripSummary]:
        url = f"{self.base_url}/rest/v1/trip_summaries"
        params = {"id": f"eq.{summary_id}", "limit": 1}
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code != 200:
            raise RuntimeError(f"Supabase fetch failed: {response.status_code}")
        data = response.json()
        if not data:
            return None
        return TripSummary(**data[0])
