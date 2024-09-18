import hashlib
import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from telethon import TelegramClient

# Replace these with your own values
api_id = "11650062"  # Your API ID
api_hash = "f4646d94267829a4ee5b57df847de074"  # Your API Hash
phone_number = "+21097542432"  # Your phone number with country code

# Create the client
client = TelegramClient("session_name", api_id, api_hash)

WEBSITES = [
    {
        "url": "https://tazkarti.com/#/matches",
        "selector": "div.container",
    },
]

CHECK_INTERVAL = 3
RECIPIENT_USERNAME = "fagvju"  # Replace with the recipient's username

async def fetch_website_content(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()

def get_div_content_hash(html, selector):
    soup = BeautifulSoup(html, "html.parser")
    div_content = soup.select_one(selector)
    if div_content:
        return hashlib.md5(div_content.get_text().strip().encode("utf-8")).hexdigest()
    return hashlib.md5(b"").hexdigest()

async def send_telegram_message(client, recipient_username, message):
    await client.send_message(recipient_username, message)

async def notify_startup(client, recipient_username):
    startup_message = "السكريبت اشتغل لو حاجه جديده نزلت هيقولك (كلام ده مبعوت من السكريبت مش مني)"
    await send_telegram_message(client, recipient_username, startup_message)

async def monitor_websites(websites):
    last_hashes = {website["url"]: None for website in websites}

    while True:
        async with ClientSession() as session:
            for website in websites:
                url = website["url"]
                selector = website["selector"]

                try:
                    content = await fetch_website_content(session, url)
                    current_hash = get_div_content_hash(content, selector)

                    if last_hashes[url] is None:
                        last_hashes[url] = current_hash
                    elif current_hash != last_hashes[url]:
                        message = f"فيه تذكرة جديده نزلت ادخل شوف الموقع: {url}"
                        print(message)
                        await send_telegram_message(client, RECIPIENT_USERNAME, message)
                        last_hashes[url] = current_hash

                except Exception as e:
                    print(f"An error occurred for {url}: {e}")

        await asyncio.sleep(CHECK_INTERVAL)

async def main():
    await client.start()
    await notify_startup(client, RECIPIENT_USERNAME)  # Send the startup message
    await monitor_websites(WEBSITES)

with client:
    client.loop.run_until_complete(main())
