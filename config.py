import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get('DISCORD_TOKEN')
WHITELIST = [int(channel_id) for channel_id in
             os.environ.get('CHANNELS_WHITELIST').split(',')]
DATABASE_URL = os.environ.get('DATABASE_URL')
