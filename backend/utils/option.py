from datetime import date, timedelta
from pprint import pprint
import schwabdev


# get next trading day
def get_next_trading_day():
    today = date.today()
    if today.weekday() == 4:
        return today + timedelta(days=3)
    else:
        return today + timedelta(days=1)


def get_option_chain(client: schwabdev.Client, ticker_symbol: str, contract_type: str):
    try:
        list_of_options = []
        next_exp_date = get_next_expiration_date(client, ticker_symbol)
        option_chain = client.option_chains(
            ticker_symbol,
            contractType=contract_type,
            includeUnderlyingQuote=False,
            strikeCount=20,
            strategy="SINGLE",
            fromDate=next_exp_date,
            toDate=next_exp_date,
        ).json()

        # for calls
        for contract in option_chain["callExpDateMap"]:
            for strike in option_chain["callExpDateMap"][contract]:
                option = option_chain["callExpDateMap"][contract][strike][0]
                symbol = option["symbol"]
                delta = option["delta"]
                strike_price = option["strikePrice"]
                last_price = option["last"]
                put_call = option["putCall"]
                description = option["description"]
                dict = {
                    "symbol": symbol,
                    "delta": delta,
                    "strike_price": strike_price,
                    "last_price": last_price,
                    "put_call": put_call,
                    "description": description,
                }
                # pprint(dict)
                list_of_options.append(dict)

        # for puts
        for contract in option_chain["putExpDateMap"]:
            for strike in option_chain["putExpDateMap"][contract]:
                option = option_chain["putExpDateMap"][contract][strike][0]
                symbol = option["symbol"]
                delta = option["delta"]
                strike_price = option["strikePrice"]
                last_price = option["last"]
                put_call = option["putCall"]
                description = option["description"]
                dict = {
                    "symbol": symbol,
                    "delta": delta,
                    "strike_price": strike_price,
                    "last_price": last_price,
                    "put_call": put_call,
                    "description": description,
                }
                # pprint(dict)
                list_of_options.append(dict)

        return list_of_options
    except Exception as e:
        pprint("Error getting option chain: " + str(e))


def get_closest_option(list_of_options: list, delta: float = 0.5):
    if list_of_options[0]["put_call"] == "PUT":
        delta = -delta
    closest_option = None
    closest_value = None
    for option in list_of_options:
        if closest_option is None:
            closest_option = option
            closest_value = abs(option["delta"] - delta)
        else:
            if abs(option["delta"] - delta) < closest_value:
                closest_option = option
                closest_value = abs(option["delta"] - delta)

    return closest_option


def get_next_expiration_date(client: schwabdev.Client, ticker_symbol: str):
    try:
        expiration_chain = client.option_expiration_chain(ticker_symbol).json()
        for expiration in expiration_chain["expirationList"]:
            if expiration["daysToExpiration"] > 0:
                chain = expiration["expirationDate"]
                break
        return chain
    except Exception as e:
        pprint("Error getting next expiration date: " + str(e))


def get_closest_expiration_date(client: schwabdev.Client, ticker_symbol: str):
    try:
        expiration_chain = client.option_expiration_chain(ticker_symbol).json()
        closest = expiration_chain["expirationList"][0]
        return closest["expirationDate"]
    except Exception as e:
        pprint("Error getting closest expiration date: " + str(e))


def get_option_contract(
    client: schwabdev.Client, ticker_symbol: str, contract_type: str, delta: float = 0.5
):
    try:
        option_chain = get_option_chain(client, ticker_symbol, contract_type)
        contract = get_closest_option(option_chain, delta)
        return contract
    except Exception as e:
        pprint("Error getting option contract: " + str(e))


def get_option_contract_price(client: schwabdev.Client, symbol: str, contract: str):
    try:
        # exmaple contract: "SPY 240826P00560000", need to parse the second part
        option_chain = get_option_chain(client, symbol, "CALL")
        option_chain.extend(get_option_chain(client, symbol, "PUT"))
        for option in option_chain:
            if option["symbol"] == contract:
                return option["last_price"]
    except Exception as e:
        pprint("Error getting option contract price: " + str(e))
