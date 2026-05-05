"""
Холодная рассылка через Telegram аккаунт @ruslan_bsag.
Для крипто-конференций: отправляет персонализированные сообщения по списку контактов.
"""
import asyncio
import csv
import os
import random
import time
from dataclasses import dataclass
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError, PeerFloodError

load_dotenv()

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION = os.environ.get("SESSION_NAME", "ruslan_bsag")

# Задержки между сообщениями (секунды) — важно для безопасности аккаунта
MIN_DELAY = 30
MAX_DELAY = 90


@dataclass
class Contact:
    username: str
    first_name: str = ""
    context: str = ""  # доп. контекст (например, с какой конференции)


MESSAGE_TEMPLATE = """Привет, {first_name}!

Видел тебя на {context} — впечатлило твоё участие в крипто-сообществе.

Мы готовим эксклюзивное мероприятие для ключевых игроков рынка. Было бы интересно пообщаться?

С уважением,
Руслан"""


def load_contacts(filepath: str) -> list[Contact]:
    contacts = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            contacts.append(Contact(
                username=row.get("username", "").strip().lstrip("@"),
                first_name=row.get("first_name", "друг").strip(),
                context=row.get("context", "конференции").strip(),
            ))
    return contacts


async def send_outreach(contacts: list[Contact], dry_run: bool = False):
    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.start()

    me = await client.get_me()
    print(f"Аккаунт: @{me.username}\nКонтактов для рассылки: {len(contacts)}\n")

    sent, failed = 0, 0

    for i, contact in enumerate(contacts, 1):
        message = MESSAGE_TEMPLATE.format(
            first_name=contact.first_name or "друг",
            context=contact.context or "конференции",
        )

        print(f"[{i}/{len(contacts)}] → @{contact.username}")

        if dry_run:
            print(f"  [DRY RUN] Сообщение:\n{message}\n")
            continue

        try:
            await client.send_message(contact.username, message)
            sent += 1
            print(f"  ✓ Отправлено")
        except UserPrivacyRestrictedError:
            failed += 1
            print(f"  ✗ Приватность не позволяет написать")
        except PeerFloodError:
            print("  ✗ Антиспам Telegram — остановка. Повторите позже.")
            break
        except FloodWaitError as e:
            print(f"  ✗ Лимит — ожидание {e.seconds}с")
            await asyncio.sleep(e.seconds)
            continue
        except Exception as e:
            failed += 1
            print(f"  ✗ Ошибка: {e}")

        if i < len(contacts):
            delay = random.randint(MIN_DELAY, MAX_DELAY)
            print(f"  Пауза {delay}с...")
            await asyncio.sleep(delay)

    await client.disconnect()
    print(f"\nИтого: отправлено {sent}, ошибок {failed}")


async def main():
    import sys
    dry_run = "--dry-run" in sys.argv
    contacts_file = "contacts.csv"

    if not os.path.exists(contacts_file):
        print(f"Файл {contacts_file} не найден. Создайте его по образцу contacts.example.csv")
        return

    contacts = load_contacts(contacts_file)
    await send_outreach(contacts, dry_run=dry_run)


if __name__ == "__main__":
    asyncio.run(main())
