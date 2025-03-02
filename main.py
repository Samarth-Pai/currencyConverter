import bumble_bencoding as bb
import requests, time, os
def scold():
    currencies_dict = get_all_currencies()
    print("Invalid currency. Supported currencies are:")
    for currency_code, currency_name in currencies_dict.items():
        print(f"{currency_code}: {currency_name}")
    exit()

def get_response(from_currency: str, to_currency: str) -> float:
    url = f"https://api.frankfurter.dev/v1/latest?base={from_currency}&symbols={to_currency}"
    response = requests.get(url)
    if response.status_code == 404:
        scold()
    response_dict = response.json()
    try:
        coeff = response_dict["rates"][to_currency]
        return coeff
    except KeyError:
        scold()

def get_dict() -> dict:
    with open("cache.bb", "rb") as f:
        return bb.decode(f.read())
    
def write_dict(currency_dict: dict) -> None:
    with open("cache.bb", "wb") as f:
        f.write(bb.encode(currency_dict))

def get_all_currencies() -> dict:
    url = "https://api.frankfurter.dev/v1/currencies"
    currencies = requests.get(url)
    currencies_dict = currencies.json() 
    return currencies_dict

def get_coefficient(from_currency: str, to_currency: str) -> float:
    if os.path.exists("cache.bb"):
        currency_dict = get_dict()
        if time.time() - currency_dict["interval"] > 3600:
            coeff = get_response(from_currency, to_currency)
            currency_dict = {
                "interval": time.time(),
                f"{from_currency}|{to_currency}": coeff
            }
            write_dict(currency_dict)
            return coeff
        else:
            try:
                return currency_dict[f"{from_currency}|{to_currency}"]
            except KeyError:
                coeff = get_response(from_currency, to_currency)
                currency_dict[f"{from_currency}|{to_currency}"] = coeff
                write_dict(currency_dict)
                return coeff
    else:
        coeff = get_response(from_currency, to_currency)
        currency_dict = {
            "interval": time.time(),
            f"{from_currency}|{to_currency}": coeff
        }   
        write_dict(currency_dict)
        return coeff
def convert(from_currency: str, to_currency: str, amount: float) -> float:
    return amount * get_coefficient(from_currency, to_currency)

if __name__=="__main__":
    from_currency = input("Enter base currency code: ").upper()
    to_currency = input("Enter the currency code to be converted: ").upper()
    amount = float(input("Enter amount: "))
    response = requests.get(f"https://api.frankfurter.dev/v1/latest?base=INR&symbols=USD,GBP")
    print(f"Converted amont: {convert(from_currency, to_currency, amount)}")