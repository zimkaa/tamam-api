import httpx
from loguru import logger

from src.settings import ADMIN_CHANNEL_ID
from src.settings import TG_TOKEN
from src.settings import TG_URL


async def send_telegram_message(text: str) -> None:
    async with httpx.AsyncClient() as client:
        method = TG_URL + TG_TOKEN + "/sendMessage"  # type: ignore
        logger.debug("send_telegram_message:")
        lst_id = ADMIN_CHANNEL_ID.split(",")  # type: ignore
        for chanel_id in lst_id:
            logger.debug(f"{chanel_id=}")
            query = await client.post(
                method,
                data={
                    "chat_id": chanel_id,  # type: ignore
                    "text": text,  # type: ignore
                },
            )
        if query.status_code != 200:
            raise Exception("Some trouble with TG")
