from __future__ import annotations

import asyncio

import httpx

from example.communication_compiler.config import AppSettings


class SpeechTranscriptionError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class AzureSpeechTranscriber:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings

    async def transcribe(self, *, audio: bytes, content_type: str, language: str) -> str:
        if not audio:
            raise SpeechTranscriptionError("EMPTY_AUDIO", "Uploaded audio is empty.")
        if len(audio) > 15 * 1024 * 1024:
            raise SpeechTranscriptionError("AUDIO_TOO_LARGE", "Uploaded audio must be 15 MB or smaller.")
        if not (self.settings.azure_speech_key or self.settings.azure_speech_resource_id):
            raise SpeechTranscriptionError("SPEECH_NOT_CONFIGURED", "AZURE_SPEECH_KEY or AZURE_SPEECH_RESOURCE_ID is required.")
        if not (self.settings.azure_speech_region or self.settings.azure_speech_endpoint):
            raise SpeechTranscriptionError("SPEECH_NOT_CONFIGURED", "AZURE_SPEECH_REGION or AZURE_SPEECH_ENDPOINT is required.")

        wav = _require_wav_audio(audio, content_type)
        endpoint = _speech_endpoint(self.settings)
        url = f"{endpoint}/speech/recognition/conversation/cognitiveservices/v1"
        params = {"language": language or "ja-JP"}
        headers = {
            "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000",
            "Accept": "application/json",
        }
        if self.settings.azure_speech_key:
            headers["Ocp-Apim-Subscription-Key"] = self.settings.azure_speech_key
        else:
            token = await asyncio.to_thread(_entra_authorization_token, self.settings.azure_speech_resource_id)
            headers["Authorization"] = f"Bearer {token}"
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(url, params=params, headers=headers, content=wav)
        if response.status_code >= 400:
            raise SpeechTranscriptionError("SPEECH_TRANSCRIPTION_FAILED", f"Azure Speech returned HTTP {response.status_code}.")

        payload = response.json()
        status = payload.get("RecognitionStatus")
        if status not in {"Success", None}:
            message = payload.get("DisplayText") or payload.get("ErrorDetails") or f"Azure Speech status: {status}"
            raise SpeechTranscriptionError("SPEECH_TRANSCRIPTION_FAILED", message)
        text = (payload.get("DisplayText") or "").strip()
        if not text:
            raise SpeechTranscriptionError("SPEECH_NO_TEXT", "No speech text was recognized.")
        return text


def _speech_endpoint(settings: AppSettings) -> str:
    if settings.azure_speech_endpoint:
        return settings.azure_speech_endpoint.rstrip("/")
    return f"https://{settings.azure_speech_region}.stt.speech.microsoft.com"


def _entra_authorization_token(resource_id: str | None) -> str:
    if not resource_id:
        raise SpeechTranscriptionError("SPEECH_NOT_CONFIGURED", "AZURE_SPEECH_RESOURCE_ID is required for Entra authentication.")
    try:
        from azure.identity import DefaultAzureCredential
    except ImportError as exc:
        raise SpeechTranscriptionError(
            "SPEECH_NOT_CONFIGURED",
            "azure-identity is required for AZURE_SPEECH_RESOURCE_ID authentication. Run with the foundry extra or set AZURE_SPEECH_KEY.",
        ) from exc

    credential = DefaultAzureCredential(exclude_interactive_browser_credential=True)
    try:
        access_token = credential.get_token("https://cognitiveservices.azure.com/.default").token
    finally:
        close = getattr(credential, "close", None)
        if close:
            close()
    return f"aad#{resource_id}#{access_token}"


def _require_wav_audio(audio: bytes, content_type: str) -> bytes:
    if "wav" not in content_type.lower():
        raise SpeechTranscriptionError("UNSUPPORTED_AUDIO_FORMAT", "Audio must be uploaded as 16 kHz mono WAV.")
    if not audio.startswith(b"RIFF") or b"WAVE" not in audio[:16]:
        raise SpeechTranscriptionError("INVALID_WAV_AUDIO", "Uploaded audio is not a valid WAV file.")
    return audio
