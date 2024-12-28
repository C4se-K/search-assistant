import hikari 
from dotenv import load_dotenv
import os

load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

print(ACCESS_TOKEN)

#bot = hikari.GatewayBot(token=ACCESS_TOKEN)