import os
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Config:

    def __init__(self):
        self.FIN_AGENT_ACCESS_TOKEN = os.getenv("FIN_AGENT_ACCESS_TOKEN")
        self.WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
        self.INTERCOM_URL = os.getenv("INTERCOM_URL", "https://api.intercom.io")
        self.INTERCOM_VERSION = os.getenv("INTERCOM_VERSION", "2.14")

        logger.info("Intercom configuration is completed...")

config = Config()