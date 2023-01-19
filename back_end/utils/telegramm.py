import httpx

from back_end import settings


async def send_telegram_message(text: str) -> None:
    async with httpx.AsyncClient() as client:
        channel_id = settings.CHANNEL_ID
        url = settings.TG_URL
        token = settings.TG_TOKEN
        url += token  # type: ignore
        method = url + "/sendMessage"
        response = await client.post(
            method,
            data={
                "chat_id": channel_id,  # type: ignore
                "text": text,  # type: ignore
            },
        )
        if response.status_code != 200:
            raise Exception("Some trouble with TG")
