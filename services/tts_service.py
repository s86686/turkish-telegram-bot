import os
import uuid

import edge_tts


async def generate_tts(
    text: str
):

    filename = (
        f"audio/{uuid.uuid4()}.mp3"
    )

    os.makedirs(
        "audio",
        exist_ok=True
    )

    communicate = edge_tts.Communicate(
        text,
        voice="tr-TR-AhmetNeural"
    )

    await communicate.save(
        filename
    )

    return filename
