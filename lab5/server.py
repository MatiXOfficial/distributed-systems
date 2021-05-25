from threading import Thread

import numpy as np
import requests
from flask import Flask, abort, request

app = Flask(__name__)


@app.route('/api/data', methods=['GET'])
def stations_data_request():
    parameter = request.args.get('parameter')
    stations = request.args.get('stations')
    if parameter is None or stations is None:
        abort(400, "Brak potrzebnych parametrów w URL (parameter, stations).")

    if stations != 'all':
        return get_stations_data_html(parameter, stations)
    else:
        return get_all_stations_data_html(parameter)


def get_stations_data_html(parameter, stations):
    stations = [station for station in stations.split(',') if station]
    stations = list(set(stations))
    date, hour = None, None
    station_data = [None] * len(stations)

    def handle_station_request(idx, station):
        nonlocal date, hour
        try:
            station_request = requests.get(f'https://danepubliczne.imgw.pl/api/data/synop/station/{station}').json()
            station_data[idx] = (station_request['stacja'], station_request[parameter])
            if idx == 0:
                date, hour = station_request['data_pomiaru'], station_request['godzina_pomiaru']
        except KeyError as e:
            if e.args[0] == 'stacja':
                abort(404, f'Nie odnaleziono stacji: {station}')
            else:
                abort(404, f'Zła nazwa parametru: {parameter}')

    threads = []
    for i, station in enumerate(stations):
        thread = Thread(target=handle_station_request, args=(i, station))
        thread.start()
        threads += [thread]

    for thread in threads:
        thread.join()

    return get_complete_html(station_data, parameter, date, hour)


def get_all_stations_data_html(parameter):
    date, hour = None, None
    station_data = []

    station_request = requests.get(f'https://danepubliczne.imgw.pl/api/data/synop').json()
    for station in station_request:
        try:
            station_data += [(station['stacja'], station[parameter])]
            if date is None:
                date, hour = station['data_pomiaru'], station['godzina_pomiaru']
        except KeyError:
            abort(404, f'Zła nazwa parametru: {parameter}')

    return get_complete_html(station_data, parameter, date, hour)


def get_complete_html(station_data, parameter, date, hour):
    station_data = list(filter(lambda x: x[1] is not None, station_data))
    data = np.array([y for x, y in station_data], dtype=float)

    return f"""
    <html lang="pl">
    <head>
        <meta charset="utf-8">
        <title>Statystyki pogody</title>
    </head>
    <body>

    <h1>{parameter.capitalize()} ({date}, {hour}:00)</h1>
    {get_statistics_html(data)}
    {get_sorted_stations_html(station_data)}

    </body>
    </html>
"""


def get_statistics_html(data):
    return f"""
<h2>Statystyki</h2>
<ul>
    <li>min = {np.min(data):0.2f}</li>
    <li>max = {np.max(data):0.2f}</li>
    <li>średnia = {np.mean(data):0.2f}</li>
    <li>mediana = {np.median(data):0.2f}</li>
    <li>odchylenie = {np.std(data):0.2f}</li>
</ul>
    """


def get_sorted_stations_html(station_data):
    station_data.sort(key=lambda x: float(x[1]))
    result = '<h2>Posortowane wyniki</h2>\n'
    result += '<ol>\n'
    for station, val in station_data:
        result += f'<li>{station}: {val}</li>\n'
    result += '</ol>'
    return result


if __name__ == '__main__':
    app.run()
