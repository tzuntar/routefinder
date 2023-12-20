from math import sin, cos, sqrt, atan2, radians

import requests

WEATHER_API_KEY = '9346e875703243688b6180606222712'
WEATHER_API_URL = 'https://api.weatherapi.com/v1/current.json?key=' + WEATHER_API_KEY
FORECAST_API_RUL = 'https://api.weatherapi.com/v1/forecast.json?key=' + WEATHER_API_KEY


def fetchForecastForCity(city, days):
    response = requests.get(f'{FORECAST_API_RUL}&q={city}&days={days}')
    if response.status_code != 200:
        print(f'Failed with code {response.status_code}')
        exit(1)
    data = response.json()
    return {
        'name': city,
        'country': data['location']['country'],
        'coords': {
            'lat': data['location']['lat'],
            'lon': data['location']['lon']
        },
        'forecast': data['forecast']['forecastday']
    }


def fetchForecastForCoords(coords, days):
    lat = coords['lat']
    lon = coords['lon']
    response = requests.get(f'{FORECAST_API_RUL}&q={lat},{lon}&days={days}')
    if response.status_code != 200:
        print(f'Failed with code {response.status_code}')
        exit(1)
    data = response.json()
    return {
        'name': data['location']['name'],  # check this
        'country': data['location']['country'],
        'coords': {
            'lat': data['location']['lat'],
            'lon': data['location']['lon']
        },
        'forecast': data['forecast']['forecastday']
    }


def rankForecast(forecast):
    score = 1.0
    score += (forecast['day']['avgtemp_c']) / 100
    score -= (forecast['day']['avghumidity']) / 100
    score -= (forecast['day']['daily_chance_of_rain']) / 100
    score -= (forecast['day']['daily_chance_of_snow']) / 100
    return score


def selectBestCityByWeather(cities, days):
    best_forecast = None
    for city in cities:
        forecast = fetchForecastForCity(city, days)
        score = rankForecast(forecast)
        if best_forecast is None or score > rankForecast(best_forecast):
            best_forecast = forecast
    return best_forecast


def distanceBetweenCoordsInKm(coord1, coord2):
    """
    Calculates the distance between two coordinates in format [lat, lon]
    and converts it to kilometers.
    """

    # approximate radius of the earth in km
    R = 6373.0

    lat1 = radians(abs(coord1['lat']))
    lon1 = radians(abs(coord1['lon']))
    lat2 = radians(abs(coord2['lat']))
    lon2 = radians(abs(coord2['lon']))

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    # here be dragons
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def findRoute(start, end, days):
    if not start or not end or not days:
        return 'Missing parameters'
    if days < 2:
        return 'Trip must be at least 2 days long'

    startCity = fetchForecastForCity(start, 1)
    endCity = fetchForecastForCity(end, days)
    distanceKm = distanceBetweenCoordsInKm(startCity['coords'], endCity['coords'])
    perDay = (distanceKm * 0.00625) / days

    latWay = 1 if endCity['coords']['lat'] > startCity['coords']['lat'] else -1
    lonWay = 1 if endCity['coords']['lon'] > startCity['coords']['lon'] else -1

    currentCoords = startCity['coords']
    forecasts = [startCity]
    for d in range(days - 2):
        currentCoords['lat'] += (perDay * latWay)
        currentCoords['lon'] += (perDay * lonWay)
        forecasts.append(fetchForecastForCoords(currentCoords, days - d))
    forecasts.append(endCity)

    return forecasts
