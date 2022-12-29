import requests
import config
from twilio.rest import Client

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

up_down = None

stock_params = {"function": "TIME_SERIES_DAILY_ADJUSTED",
                "symbol": STOCK_NAME,
                "apikey": config.STOCK_API_KEY,
                }

stock_response = requests.get(url=STOCK_ENDPOINT, params=stock_params)
stock_response.raise_for_status()
stock_data = stock_response.json()["Time Series (Daily)"]
stock_data_list = [value for (key, value) in stock_data.items()]

yesterday_closing = float(stock_data_list[0]["4. close"])
before_yesterday_closing = float(stock_data_list[1]["4. close"])

difference = yesterday_closing - before_yesterday_closing

if difference > 0:
    up_down = "🔺"
else:
    up_down = "🔻"

percentual_variation = round((abs(difference) / yesterday_closing) * 100, 2)

if percentual_variation > 5:
    news_params = {"q": COMPANY_NAME,
                   "language": "en",
                   "apiKey": config.NEWS_API_KEY,
                   "sortBy": "publishedAt",
                   }
    news_response = requests.get(url=NEWS_ENDPOINT, params=news_params)
    news_data = news_response.json()["articles"][:3]
    formatted_articles = [f"Headline: {article['title']}. \nBrief: {article['description']}" for article in news_data]

    account_sid = config.TW_ACCOUNT_SID
    auth_token = config.TW_AUTH_TOKEN
    client = Client(account_sid, auth_token)

    for article in formatted_articles:
        message = client.messages \
            .create(
                body=f"{STOCK_NAME}: {up_down} {percentual_variation}%\n{article}",
                from_=config.TW_PHONE,
                to=config.MY_PHONE_NUMBER
            )
        print(message.status)
