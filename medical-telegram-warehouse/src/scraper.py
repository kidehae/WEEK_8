# src/scraper.py
import os
import json
import asyncio
from datetime import datetime, timezone
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from utils import get_logger, load_dotenv

# Instantiate custom logger
logger = get_logger("TelegramScraper")

# Define Target Channels assigned by target scope (Fixed CheMed handle)
CHANNELS_TO_SCRAPE = [
    "CheMed123",            # Corrected public handle
    "lobelia4cosmetics",  
    "tikvahpharma"       
]

# Throttling parameters to preserve pipeline health
MESSAGE_DELAY = 0.2  # slightly lowered to speed up but remain polite
CHANNEL_DELAY = 3.0  

async def scrape_channel(client: TelegramClient, channel_username: str, limit: int = 100):
    logger.info(f"Beginning ingestion workflow for channel: @{channel_username}")
    scraped_messages = []
    
    try:
        # Get the entity first to verify access
        entity = await client.get_entity(channel_username)
        
        async for message in client.iter_messages(entity, limit=limit):
            try:
                # Fixed the timezone conversion bug using .replace() or .astimezone()
                if message.date:
                    msg_date = message.date.astimezone(timezone.utc)
                else:
                    msg_date = datetime.now(timezone.utc)
                    
                date_str = msg_date.strftime("%Y-%m-%d")
                
                # Setup internal image payload trackers
                has_media = False
                image_relative_path = None
                
                # Check for explicit downloadable photo elements
                if message.photo:
                    has_media = True
                    img_dir = f"data/raw/images/{channel_username}"
                    os.makedirs(img_dir, exist_ok=True)
                    img_filename = f"{message.id}.jpg"
                    image_relative_path = os.path.join(img_dir, img_filename)
                    
                    # Atomic download execution block
                    logger.info(f"Downloading binary media asset for Message ID: {message.id} from @{channel_username}")
                    await message.download_media(file=image_relative_path)
                
                # Map extracted message fields directly to target data layer schema variables
                message_payload = {
                    "message_id": message.id,
                    "channel_name": channel_username,
                    "message_date": msg_date.isoformat(),
                    "message_text": message.text if message.text else "",
                    "has_media": has_media,
                    "image_path": image_relative_path,
                    "views": message.views if message.views else 0,
                    "forwards": message.forwards if message.forwards else 0
                }
                
                scraped_messages.append(message_payload)
                await asyncio.sleep(MESSAGE_DELAY)
                
            except FloodWaitError as fwe:
                logger.warning(f"Encountered rate limit constraints. Enforcing immediate back-off for {fwe.seconds}s.")
                await asyncio.sleep(fwe.seconds)
            except Exception as item_err:
                logger.error(f"Failed parsing message snapshot on ID {getattr(message, 'id', 'Unknown')}: {str(item_err)}")
                
        # Commit Data Lake write partition tasks grouped atomically by runtime partition layout (YYYY-MM-DD)
        if scraped_messages:
            current_date_partition = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            partition_dir = f"data/raw/telegram_messages/{current_date_partition}"
            os.makedirs(partition_dir, exist_ok=True)
            
            output_file = os.path.join(partition_dir, f"{channel_username}.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(scraped_messages, f, ensure_ascii=False, indent=4)
                
            logger.info(f"Successfully sealed {len(scraped_messages)} entries into partition: {output_file}")
        else:
            logger.warning(f"No active message payloads fetched or stored for channel: @{channel_username}")
            
    except Exception as channel_err:
        logger.error(f"Fatal disruption processing public channel feed @{channel_username}: {str(channel_err)}")

async def main():
    api_id = os.getenv("TG_API_ID")
    api_hash = os.getenv("TG_API_HASH")
    
    if not api_id or not api_hash:
        logger.critical("Initialization aborted: Missing TG_API_ID or TG_API_HASH parameters in local environment context.")
        return

    # Telethon re-uses your authenticated session file automatically
    async with TelegramClient("session_kara_consulting", int(api_id), api_hash) as client:
        logger.info("Telethon authorization handshake validated successfully.")
        
        for target_channel in CHANNELS_TO_SCRAPE:
            await scrape_channel(client, target_channel, limit=100)
            logger.info(f"Pausing workflow for {CHANNEL_DELAY}s between adjacent domain profiles.")
            await asyncio.sleep(CHANNEL_DELAY)

if __name__ == "__main__":
    asyncio.run(main())