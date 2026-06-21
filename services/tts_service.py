import os
import uuid

import edge_tts


async def generate_tts(
    text: str,
    language: str = "tr"
):

    filename = (
        f"audio/{uuid.uuid4()}.mp3"
    )

    os.makedirs(
        "audio",
        exist_ok=True
    )

    if language == "en":

        voice = "en-US-GuyNeural"

    else:

        voice = "tr-TR-AhmetNeural"

    communicate = edge_tts.Communicate(
        text,
        voice=voice
    )

    await communicate.save(
        filename
    )

    return filename
