import httpx

from src import settings


async def send_telegram_message(text: str) -> None:
    async with httpx.AsyncClient() as client:
        method = settings.TG_URL + settings.TG_TOKEN + "/sendMessage"  # type: ignore
        response = await client.post(
            method,
            data={
                "chat_id": settings.CHANNEL_ID,
                "text": text,
            },
        )
        if response.status_code != 200:
            raise Exception("Some trouble with TG")
