"""
Читает последние сообщения из указанных чатов и сохраняет в файл для анализа.
"""
import asyncio
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import User, Chat, Channel

load_dotenv()

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION = os.environ.get("SESSION_NAME", "ruslan_bsag")

CHATS_TO_READ = [
    "iTor_0x",
    "Ivan_ICODA",
    "avicoda",
]

KEYWORDS = ["kaching", "качинг", "kach"]
MESSAGES_LIMIT = 100


async def get_chat_messages(client, chat_id, limit=100):
    messages = []
    try:
        entity = await client.get_entity(chat_id)
        async for msg in client.iter_messages(entity, limit=limit):
            if msg.text:
                sender = ""
                if msg.sender:
                    if hasattr(msg.sender, 'username') and msg.sender.username:
                        sender = f"@{msg.sender.username}"
                    elif hasattr(msg.sender, 'first_name'):
                        sender = msg.sender.first_name or "Unknown"
                messages.append({
                    "date": msg.date.strftime("%Y-%m-%d %H:%M"),
                    "sender": sender,
                    "text": msg.text
                })
        return messages
    except Exception as e:
        print(f"  Ошибка при чтении {chat_id}: {e}")
        return []


async def find_kaching_dialog(client):
    """Ищет диалог с Kaching в названии."""
    print("Ищу чат Kaching <> ICODA...")
    async for dialog in client.iter_dialogs():
        name = dialog.name or ""
        if any(k in name.lower() for k in KEYWORDS):
            print(f"  Найден: {name}")
            messages = []
            async for msg in client.iter_messages(dialog.entity, limit=MESSAGES_LIMIT):
                if msg.text:
                    sender = ""
                    if msg.sender:
                        if hasattr(msg.sender, 'username') and msg.sender.username:
                            sender = f"@{msg.sender.username}"
                        elif hasattr(msg.sender, 'first_name'):
                            sender = msg.sender.first_name or "Unknown"
                    messages.append({
                        "date": msg.date.strftime("%Y-%m-%d %H:%M"),
                        "sender": sender,
                        "text": msg.text
                    })
            return name, messages
    return None, []


async def main():
    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.start()

    all_data = {}

    # Читаем чат Kaching <> ICODA
    name, messages = await find_kaching_dialog(client)
    if messages:
        all_data[name] = messages
        print(f"  Загружено {len(messages)} сообщений")
    else:
        print("  Чат Kaching не найден")

    # Читаем личные чаты
    for username in CHATS_TO_READ:
        print(f"Читаю @{username}...")
        msgs = await get_chat_messages(client, username, MESSAGES_LIMIT)
        if msgs:
            all_data[f"@{username}"] = msgs
            print(f"  Загружено {len(msgs)} сообщений")

    await client.disconnect()

    # Сохраняем в файл
    output_file = "chats_export.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"\nГотово! Данные сохранены в {output_file}")
    print(f"Всего чатов: {len(all_data)}")
    for chat, msgs in all_data.items():
        print(f"  {chat}: {len(msgs)} сообщений")

    # Выводим последние сообщения для быстрого просмотра
    print("\n" + "="*60)
    print("ПОСЛЕДНИЕ СООБЩЕНИЯ:")
    print("="*60)
    for chat, msgs in all_data.items():
        print(f"\n--- {chat} ---")
        for msg in msgs[:20]:
            print(f"[{msg['date']}] {msg['sender']}: {msg['text'][:200]}")


if __name__ == "__main__":
    asyncio.run(main())
