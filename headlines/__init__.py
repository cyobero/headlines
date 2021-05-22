import feedparser
import json
import urllib

from flask import Flask, render_template, request

app = Flask(__name__)

RSS_FEEDS = {
    'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
    'cnn': 'http://rss.cnn.com/rss/edition.rss',
    'fox': 'http://feeds.foxnews.com/foxnews/latest',
    'iol': 'http://iol.co.za/cmlink/1.640'
}

DEFAULTS = {'publication': 'bbc',
            'city': 'London, UK',
            'currency_from': 'USD',
            'currency_to': 'EUR'}

WEATHER_APP_ID = '758501f8c3d9c9c51884c5e7bee1e523'
CURRENCY_APP_ID = '1dbf2bb23f364a0890aca9f39215e95b'

WEATHER_URL ='http://api.openweathermap.org/data/2.5/weather?q={0}&units=imperial&appid={1}'
CURRENCY_URL = 'https://openexchangerates.org/api/latest.json?app_id={}'.format(
    CURRENCY_APP_ID)


def get_rate(currency1, currency2):
    """Returns the exchange of two different currencies."""
    all_currency = urllib.request.urlopen(CURRENCY_URL).read()
    parsed = json.loads(all_currency).get('rates')
    currency1_rate = parsed.get(currency1.upper())
    currency2_rate = parsed.get(currency2.upper())
    return currency1_rate/currency2_rate


def get_weather(query):
    """Returns the current weather (in fahrenheit) of a given city."""
    query = urllib.parse.quote(query)
    url = WEATHER_URL.format(query, WEATHER_APP_ID)
    data = urllib.request.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get('weather'):
        weather = {'description': parsed['weather'][0]['description'],
                   'temperature': parsed['main']['temp'],
                   'city': parsed['name'],
                   'country': parsed['sys']['country']}
    return weather


def get_news(query):
    """
    Returns RSS feed for given publication.
    """
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS['publication']
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']


@app.route('/')
def home():
    publication = request.args.get('publication')
    if not publication:
        publication = DEFAULTS['publication']
    articles = get_news(publication)

    city = request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)

    currency_from = request.args.get('currency_from')
    if not currency_from:
        currency_from = DEFAULTS['currency_from']
    currency_to = request.args.get('currency_to')
    if not currency_to:
        currency_to = DEFAULTS['currency_to']
    rate = get_rate(currency_from, currency_to)
    return render_template('index.html', articles=articles, weather=weather,
                           currency_from=currency_from, currency_to=currency_to, rate=rate)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
