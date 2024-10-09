import hashlib
import asyncio
import webbrowser  # This will open the SMS app with the message ready to be sent
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import urllib.parse

# Replace this with the recipient's phone number
recipient_number = "+21097542432"  # Phone number in international format (with country code)

WEBSITES = [
    {
        "url": "https://tazkarti.com/#/matches",
        "selector": "div.container",
    },
]

CHECK_INTERVAL = 3  # seconds

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

def open_sms(phone_number, message):
    # Encode the message for URL formatting
    encoded_message = urllib.parse.quote(message)
    # Create the SMS URI scheme to open the SMS app
    sms_url = f"sms:{phone_number}?body={encoded_message}"
    # Open the URL to launch the SMS app with the message ready to be sent
    webbrowser.open(sms_url)

async def notify_startup():
    startup_message = "The script has started. You will be notified if anything new is detected (automated message)."
    open_sms(recipient_number, startup_message)

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
                        message = f"New ticket available, check the website: {url}"
                        print(message)
                        open_sms(recipient_number, message)
                        last_hashes[url] = current_hash

                except Exception as e:
                    print(f"An error occurred for {url}: {e}")

        await asyncio.sleep(CHECK_INTERVAL)

async def main():
    await notify_startup()  # Send the startup message
    await monitor_websites(WEBSITES)

if __name__ == "__main__":
    asyncio.run(main())
