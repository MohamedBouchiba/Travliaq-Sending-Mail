import json
from datetime import datetime
from typing import Optional
from app.core.config import get_settings
from app.services.llm_client import LLMClient
from app.services.supabase_client import TripSummary


def format_date(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).strftime("%B %d, %Y")
    except ValueError:
        return value


def choose_template(summary: TripSummary) -> str:
    persona = (summary.persona or "").lower()
    travel_style = (summary.travel_style or "").lower()
    rhythm = (summary.rhythm or "").lower()
    total_days = summary.total_days or 0
    total_price = summary.total_price or 0
    travelers = summary.travelers_count or 1
    if "family" in persona or travelers > 2:
        return "family"
    if "romantic" in persona or "romantic" in travel_style:
        return "romantic"
    if total_days and total_days <= 4:
        return "city_break"
    if total_price and total_price < 500:
        return "budget"
    if "adventure" in travel_style or "explorer" in persona or "fast" in rhythm:
        return "explorer"
    return "explorer"


def build_prompt(summary: TripSummary, frontend_url: str) -> list[dict]:
    template_guides = {
        "explorer": "Explorer / adventurous trip: energetic tone, highlights unique experiences, discovery, and momentum.",
        "romantic": "Chill & romantic escape: warm tone, relaxation, ambiance, focus on hotel and slow pace.",
        "family": "Family trip: reassuring tone, clear logistics, kid-friendly activities and pacing.",
        "budget": "Budget-conscious traveler: emphasize smart choices, value, and transparency on prices.",
        "city_break": "Short city break: concise, energetic, quick hits for a weekend or 3-4 day stay.",
    }
    template = choose_template(summary)
    
    # ✅ FIX: Use trip_code if available, fallback to questionnaire_id
    identifier = summary.trip_code if summary.trip_code else summary.questionnaire_id
    print(f"DEBUG: Building link with identifier: '{identifier}' (trip_code: {summary.trip_code}, q_id: {summary.questionnaire_id})")
    trip_link = f"{str(frontend_url).rstrip('/')}/{identifier}"
    
    content = {
        "id": str(summary.id),
        "questionnaire_id": str(summary.questionnaire_id),
        "trip_code": summary.trip_code,  # Added to context
        "user_email": summary.user_email,
        "persona": summary.persona,
        "travelers_count": summary.travelers_count,
        "destination": summary.destination,
        "destination_en": summary.destination_en,
        "country_code": summary.country_code,
        "start_date": format_date(summary.start_date),
        "end_date": format_date(summary.end_date),
        "total_days": summary.total_days,
        "total_nights": summary.total_nights,
        "travel_style": summary.travel_style,
        "rhythm": summary.rhythm,
        "average_weather": summary.average_weather,
        "summary_paragraph": summary.summary_paragraph,
        "activities_summary": summary.activities_summary,
        "steps_count": summary.steps_count,
        "budget": {
            "total_price": summary.total_price,
            "price_flights": summary.price_flights,
            "price_hotels": summary.price_hotels,
            "price_activities": summary.price_activities,
            "currency": summary.budget_currency,
        },
        "transport": {
            "flight_from": summary.flight_from,
            "flight_to": summary.flight_to,
            "flight_duration": summary.flight_duration,
            "hotel_name": summary.hotel_name,
            "hotel_rating": summary.hotel_rating,
        },
        "media": {
            "main_image_url": str(summary.main_image_url) if summary.main_image_url else None,
            "gallery_urls": summary.gallery_urls,
        },
        "call_to_action_url": trip_link,
    }
    
    system_prompt = (
        "You are an expert email designer and copywriter for a premium travel agency. "
        "Your task is to generate a JSON response containing the subject, preheader, text body, and a HIGHLY RESPONSIVE HTML body. "
        "You must prioritize mobile responsiveness, premium aesthetics, and creative emoji usage."
    )
    
    user_prompt = {
        "template_selected": template,
        "template_instructions": template_guides[template],
        "templates_available": template_guides,
        "trip_summary": content,
        "requirements": {
            "subject": "Compelling subject line with destination and 1-2 creative emojis (not generic ones).",
            "preheader": "Teasing inbox preview.",
            "text_body": "Plain text version.",
            "html_body": {
                "design_guidelines": [
                    "MOBILE FIRST: The email must look perfect on mobile devices.",
                    "Use a single-column layout with max-width: 600px centered.",
                    "Use large, touch-friendly buttons for the CTA.",
                    "Use premium fonts (system stack: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif).",
                    "Use soft shadows, rounded corners (msg-like bubbles), and whitespace for a modern feel.",
                    "Header image should be responsive (width: 100%, height: auto)."
                ],
                "emoji_style": [
                    "Use ORIGINAL, varied, and creative emojis.",
                    "Do NOT use generic emojis like ✈️, 🌍, 📅 repeatedly.",
                    "Use emojis that match the specific destination vibe (e.g., 🥐/🍷 for France, 🏯/🌸 for Japan).",
                    "Place emojis strategically in headers or highlights."
                ],
                "structure": [
                    "Hero Image (main_image_url)",
                    "Modern Header with 'Your Trip to [Destination]'",
                    "Personalized Greeting",
                    "Trip Highlights & Stats (Days, Budget, Style) in a grid or cards",
                    "Detailed 'Why you'll love it' section",
                    "Budget breakdown (if available) in a clean table or list",
                    "Prominent CTA Button ('Discover My Trip') linking to call_to_action_url",
                    "Footer with agency signature"
                ],
                "tone": "Premium, exciting, personalized, and visually 'wow'."
            },
            "output_format": "Return JSON object with subject, preheader, text_body, html_body only"
        },
    }
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json_dumps(user_prompt)},
    ]


def json_dumps(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False)


def generate_email(summary: TripSummary) -> dict:
    settings = get_settings()
    llm_client = LLMClient()
    messages = build_prompt(summary, settings.frontend_trip_base_url)
    return llm_client.generate_email_content(messages)
