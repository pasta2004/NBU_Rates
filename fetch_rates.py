import requests

def fetch_rates_from_api(date_str=None):
    if date_str:
        formatted = date_str.replace("-", "")
        url = f"https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?date={formatted}&json"
    else:
        url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"

    response = requests.get(url)
    return response.json()