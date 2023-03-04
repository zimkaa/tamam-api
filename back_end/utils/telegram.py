import httpx
from loguru import logger

from back_end.settings import ADMIN_CHANNEL_ID
from back_end.settings import CHANNEL_ID
from back_end.settings import TG_TOKEN
from back_end.settings import TG_URL


# async def send_telegram_message(text: str) -> None:
#     async with httpx.AsyncClient() as client:
#         method = settings.TG_URL + settings.TG_TOKEN + "/sendMessage"  # type: ignore
#         response = await client.post(
#             method,
#             data={
#                 "chat_id": settings.CHANNEL_ID,
#                 "text": text,
#             },
#         )
#         if response.status_code != 200:
#             raise Exception("Some trouble with TG")


async def send_telegram_message(text: str) -> None:
    async with httpx.AsyncClient() as client:
        method = TG_URL + TG_TOKEN + "/sendMessage"  # type: ignore
        logger.debug("send_telegram_message:")
        lst_id = ADMIN_CHANNEL_ID.split(",")
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
