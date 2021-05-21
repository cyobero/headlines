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


def get_weather(query):
    query = urllib.parse.quote(query)
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=758501f8c3d9c9c51884c5e7bee1e523'.format(query)
    data = urllib.request.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get('weather'):
        weather = {'description': parsed['weather'][0]['description'],
                   'temperature': parsed['main']['temp'],
                   'city': parsed['name']}
    return weather


@app.route('/')
def get_news(publication="bbc"):
    """
    Returns RSS feed for given publication.
    """
    query = request.args.get("publication")
    if not query or query.lower() not in RSS_FEEDS:
        publication = "bbc"
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    weather = get_weather('Chicago, IL, USA')
    return render_template("index.html", articles=feed['entries'], weather=weather)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
