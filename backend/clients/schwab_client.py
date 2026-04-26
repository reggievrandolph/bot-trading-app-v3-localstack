from config import CS_APP_KEY, CS_APP_SECRET, CS_CALLBACK_URL
import schwabdev


def get_client():
    try:
        # Create a new session, credentials path is required.
        client = schwabdev.Client(CS_APP_KEY, CS_APP_SECRET)  # create a client

        client.update_tokens_auto()  # start the auto access token updater
        print("\033c")
        return client
    except Exception as e:
        print(f"Error: {e}")
