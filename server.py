import json

from flask import Flask, request, render_template
from cities import findRoute

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def route():
    error = None
    if request.method == 'POST':
        start = request.form['start']
        end = request.form['end']
        days = request.form['days']
        route = findRoute(start, end, int(days))
        link = 'https://www.google.com/maps/dir/'
        for city in route:
            link += city['name'] + '/'
        return render_template('results.html', cities=route, link=link)
    return render_template('index.html')
