# Standard libraries
import threading
from datetime import datetime, timedelta
import requests

# 3rd party dependencies
import pandas as pd  # For parsing data
from kucoin.client import Client

# Local dependencies
from kucoin_keys import api_key, api_secret, api_passphrase, bot_token, send_to

client = Client(api_key, api_secret, api_passphrase)


def send_alert(bot_message):
    """ 
    Sending message via Telegram 
    @param bot_message: string including the text that the telegram account should receive
    """
    # For displaying in console
    print(
        " ".join(
            [bot_message.replace("%25", "%"), "at", datetime.now().strftime("%H:%M:%S")]
        )
    )

    # Send it via Telegram
    requests.get(
        "https://api.telegram.org/bot"
        + bot_token
        + "/sendMessage?chat_id="
        + send_to
        + "&parse_mode=HTML&text="
        + bot_message
    )


def get_orders():

    # Get difference between now and last call
    time = datetime.utcnow() - timedelta(seconds=60)

    # Get orders that happened during this interval
    try:
        orders = pd.DataFrame(client.get_orders()["items"])
        orders["createdAt"] = pd.to_datetime(orders["createdAt"], unit="ms")
        orders = orders.loc[
            (orders["stopTriggered"] == True) & (orders["createdAt"] > time)
        ]

        # Send a message if there are orders
        if not orders.empty:
            for _, row in orders.iterrows():
                send_alert(f"Sold {(row['symbol'])} for ${(row['price'])}")
    except Exception as e:
        print(e)
        print(f"Error in get_orders at {datetime.now()}")
        
    # Start threading
    threading.Timer(60.0, get_orders).start()


if __name__ == "__main__":
    print("Starting...")
    get_orders()
