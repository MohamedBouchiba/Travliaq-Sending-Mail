from uuid import UUID
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.services.supabase_client import SupabaseClient
from app.services.email_builder import generate_email
from app.services.resend_client import ResendClient


router = APIRouter()


class SendEmailRequest(BaseModel):
    summary_id: UUID


class SendEmailSuccessResponse(BaseModel):
    ok: bool
    email_id: str
    summary_id: UUID


class ErrorResponse(BaseModel):
    ok: bool
    error: str
    detail: str


@router.post("/send-trip-summary-email", response_model=SendEmailSuccessResponse, responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def send_trip_summary_email(payload: SendEmailRequest):
    supabase_client = SupabaseClient()
    summary = supabase_client.fetch_trip_summary(payload.summary_id)
    if not summary:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"ok": False, "error": "SUMMARY_NOT_FOUND", "detail": "Trip summary not found"})
    # ✅ Accepter SUCCESS aussi (pas seulement COMPLETED/READY/DONE)
    if summary.pipeline_status and summary.pipeline_status.upper() not in {"SUCCESS", "COMPLETED", "READY", "DONE"}:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"ok": False, "error": "SUMMARY_NOT_READY", "detail": f"Trip summary status is '{summary.pipeline_status}', not SUCCESS"})
    try:
        email_content = generate_email(summary)
        email_id = ResendClient().send_email(
            to=summary.user_email,
            subject=email_content.get("subject", "Your trip"),
            html_body=email_content.get("html_body", ""),
            text_body=email_content.get("text_body", ""),
        )
        return SendEmailSuccessResponse(ok=True, email_id=email_id, summary_id=summary.id)
    except Exception as exc:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"ok": False, "error": "INTERNAL_ERROR", "detail": str(exc)})
