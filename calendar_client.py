"""
calendar_client.py
Gestión de citas en Google Calendar usando la misma autenticación OAuth2 que Gmail.
"""

import json
import logging
import os
from datetime import datetime, timedelta

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

CALENDAR_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
]

CALENDAR_ID = os.environ.get("GOOGLE_CALENDAR_ID", "primary")
EVENT_DURATION_MINUTES = int(os.environ.get("EVENT_DURATION_MINUTES", "60"))


def get_calendar_service():
    """
    Reutiliza las credenciales OAuth2 de Gmail añadiendo el scope de Calendar.
    Usa la misma variable de entorno GMAIL_CREDENTIALS_JSON.
    """
    creds_data = json.loads(os.environ["GMAIL_CREDENTIALS_JSON"])
    creds = Credentials(
        token=creds_data.get("token"),
        refresh_token=creds_data.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=creds_data.get("client_id"),
        client_secret=creds_data.get("client_secret"),
        scopes=CALENDAR_SCOPES,
    )
    if not creds.valid:
        if creds.refresh_token:
            creds.refresh(Request())
        else:
            raise RuntimeError("Credenciales de Google inválidas y sin refresh_token.")
    return build("calendar", "v3", credentials=creds)


def agendar_cita(fecha_hora: datetime, email_cliente: str, asunto_email: str) -> str | None:
    """
    Crea un evento en Google Calendar y devuelve el event_id.
    Devuelve None si falla.

    Args:
        fecha_hora: Datetime del inicio de la cita (sin timezone → se asume UTC).
        email_cliente: Email del cliente para invitarlo al evento.
        asunto_email: Asunto del email original (se usa como título del evento).
    """
    try:
        svc = get_calendar_service()

        inicio = fecha_hora
        fin = fecha_hora + timedelta(minutes=EVENT_DURATION_MINUTES)

        evento = {
            "summary": f"Cita: {asunto_email[:80]}",
            "description": f"Cita agendada automáticamente para {email_cliente}.",
            "start": {
                "dateTime": inicio.strftime("%Y-%m-%dT%H:%M:%S"),
                "timeZone": "Europe/Madrid",
            },
            "end": {
                "dateTime": fin.strftime("%Y-%m-%dT%H:%M:%S"),
                "timeZone": "Europe/Madrid",
            },
            "attendees": [{"email": email_cliente}],
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 24 * 60},
                    {"method": "popup", "minutes": 30},
                ],
            },
        }

        resultado = svc.events().insert(
            calendarId=CALENDAR_ID,
            body=evento,
            sendUpdates="all",  # Envía invitación al cliente
        ).execute()

        event_id = resultado.get("id")
        logger.info(f"📅 Cita agendada en Calendar | event_id: {event_id} | {inicio}")
        return event_id

    except Exception as e:
        logger.error(f"❌ Error agendando cita en Calendar: {e}")
        return None


def cancelar_cita(event_id: str) -> bool:
    """
    Elimina un evento de Google Calendar por su event_id.
    Devuelve True si tuvo éxito, False si falló.
    """
    try:
        svc = get_calendar_service()
        svc.events().delete(
            calendarId=CALENDAR_ID,
            eventId=event_id,
            sendUpdates="all",  # Notifica al cliente de la cancelación
        ).execute()
        logger.info(f"🗑️ Evento eliminado de Calendar | event_id: {event_id}")
        return True
    except Exception as e:
        logger.error(f"❌ Error cancelando cita en Calendar: {e}")
        return False
