"""
Авторизация Telegram аккаунта @ruslan_bsag.
Запустить один раз для создания файла сессии.
"""
import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

load_dotenv()

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
PHONE = os.environ["TELEGRAM_PHONE"]
SESSION = os.environ.get("SESSION_NAME", "ruslan_bsag")


async def authorize():
    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(PHONE)
        code = input("Введите код из Telegram: ")
        try:
            await client.sign_in(PHONE, code)
        except SessionPasswordNeededError:
            password = input("Введите пароль 2FA: ")
            await client.sign_in(password=password)

    me = await client.get_me()
    print(f"Авторизован как: @{me.username} ({me.first_name})")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(authorize())
