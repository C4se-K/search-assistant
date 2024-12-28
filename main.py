import os 
import time
import socket
from dotenv import load_dotenv

from hikari_disc_interface import hiakri_discord_interface


def main():

    load_dotenv()
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
    #print(ACCESS_TOKEN)

    bot_instance = hiakri_discord_interface(ACCESS_TOKEN)
    bot_instance.start()


    

if __name__ == "__main__":
    main()



