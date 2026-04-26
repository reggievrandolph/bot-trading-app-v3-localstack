from datetime import datetime
from pprint import pprint

import pytz


def get_time():
    try:
        eastern = pytz.timezone("US/Eastern")
        formatted_time = datetime.now(eastern).strftime("%H:%M:%S %Y-%m-%d")
        return formatted_time
    except Exception as e:
        pprint(f"Error getting time: {e}")
