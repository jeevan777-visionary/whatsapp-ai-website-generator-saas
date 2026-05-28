from __future__ import annotations

from ai.translator import t
from database.repository import get_or_create_user, track_event
from tasks.generation_tasks import enqueue_website_request_async
from utils.helpers import generate_request_id
from whatsapp.client import WhatsAppClient
from whatsapp.command_parser import is_edit_command
from whatsapp.sessions import get_session, upsert_session

whatsapp_client = WhatsAppClient()


def handle_incoming_message(user_number: str, body: str) -> str:
    user = get_or_create_user(user_number)
    language = user.language or "en"
    session = get_session(user_number)
    is_edit = is_edit_command(body)

    if is_edit and session.request_id:
        request_id = session.request_id
        track_event("edit_command", request_id, user_number, {"message": body})
        whatsapp_client.send_message(user_number, t("generating", language))
        enqueue_website_request_async(request_id, user_number, body, is_edit=True)
        upsert_session(user_number=user_number, message=body, request_id=request_id)
        return request_id

    request_id = generate_request_id()
    upsert_session(user_number=user_number, message=body, request_id=request_id)
    track_event("new_request", request_id, user_number)
    whatsapp_client.send_message(user_number, t("generating", language))
    enqueue_website_request_async(request_id, user_number, body, is_edit=False)
    return request_id


def handle_voice_message(user_number: str, media_url: str) -> str:
    from ai.transcription import transcribe_audio_url

    transcript = transcribe_audio_url(media_url)
    if not transcript:
        whatsapp_client.send_message(user_number, "Could not transcribe voice note. Please send text.")
        return ""
    return handle_incoming_message(user_number, transcript)
