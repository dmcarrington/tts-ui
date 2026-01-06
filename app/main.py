import io
import zipfile
import edge_tts
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Text-to-Speech Converter")

# Serve static files (frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Serve the main page."""
    return FileResponse("static/index.html")


@app.get("/api/voices")
async def list_voices():
    """List available TTS voices."""
    voices = await edge_tts.list_voices()
    # Return simplified voice data, sorted by locale then name
    result = [
        {
            "name": v["ShortName"],
            "gender": v["Gender"],
            "locale": v["Locale"],
            "language": v["Locale"].split("-")[0],
        }
        for v in voices
    ]
    result.sort(key=lambda x: (x["locale"], x["name"]))
    return result


@app.post("/api/convert")
async def convert_text_to_speech(
    text: str = Form(...),
    voice: str = Form("en-US-ChristopherNeural"),
    subtitles: bool = Form(False)
):
    """Convert text to MP3 speech using edge-tts, optionally with subtitles."""
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    if len(text) > 10000:
        raise HTTPException(status_code=400, detail="Text too long (max 10000 characters)")

    try:
        # Generate speech using selected voice
        # Use WordBoundary for word-level subtitle timing
        communicate = edge_tts.Communicate(
            text.strip(),
            voice=voice,
            boundary="WordBoundary" if subtitles else "SentenceBoundary"
        )
        submaker = edge_tts.SubMaker() if subtitles else None

        # Collect audio data in memory
        audio_data = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])
            elif submaker and chunk["type"] == "WordBoundary":
                submaker.feed(chunk)

        audio_data.seek(0)

        # If subtitles requested, return a zip file with both MP3 and SRT
        if subtitles:
            srt_content = submaker.get_srt()

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("speech.mp3", audio_data.read())
                zf.writestr("speech.srt", srt_content)

            zip_buffer.seek(0)

            return Response(
                content=zip_buffer.read(),
                media_type="application/zip",
                headers={
                    "Content-Disposition": "attachment; filename=speech.zip"
                }
            )

        # Return just the MP3
        return Response(
            content=audio_data.read(),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS conversion failed: {str(e)}")
