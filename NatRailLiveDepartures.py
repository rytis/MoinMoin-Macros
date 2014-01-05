#!/usr/bin/env python

import os
import re
import csv
import json
import copy
import pprint
import difflib
import jinja2
import requests


def get_all_stops(service_id):
    url = "http://ojp.nationalrail.co.uk/service/ldbdetailsJson?departing=true&liveTrainsFrom=&liveTrainsTo=&serviceId={service_id}".format(service_id=service_id)
    r = requests.get(url)
    return r.json()['trains']


def build_stations_dictionary():
    stations = {}
    station_codes_file = os.path.join(os.path.dirname(__file__), "data", "NatRailLiveDepartures_station_data.csv")
    with open(station_codes_file, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            stations[row[0]] = row[1]
    return stations


def fuzzy_match_station_name_against_code(station_name, station_code):
    stations = build_stations_dictionary()
    if station_name in stations:
        similar_name = station_name
    else:
        similar_name = difflib.get_close_matches(station_name, stations.keys(), 1)[0]
    if similar_name:
        return stations[similar_name] == station_code
    else:
        return False


def find_time_at_destination(service_id, station_code):
    all_stops = get_all_stops(service_id)
    for stop in all_stops:
        if fuzzy_match_station_name_against_code(stop[2], station_code):
            if stop[4]:
                return "{time} ({status})".format(time=stop[3], status=stop[4])
            else:
                return stop[1]
    return ''


def add_time_at_destination(train_data, station_code, max_lookups=3):
    result = copy.deepcopy(train_data)
    result['trains'] = []
    cnt = 0
    for t in train_data['trains']:
        new_train_data = t[:]
        if cnt < max_lookups:
            time_at_destination = find_time_at_destination(t[5], station_code)
            new_train_data.append(time_at_destination)
        result['trains'].append(new_train_data)
        cnt += 1
    return result


def cleanup_data(train_data):
    result = copy.deepcopy(train_data)
    result['trains'] = []
    for t in train_data['trains']:
        status = t[3].replace('&lt;br/&gt;', '-')
        service_id = re.search('^/service/ldbdetails/(.+)\?f=.+', t[5]).group(1)
        new_train_data = [t[0], t[1], t[2], status, t[4], service_id]
        result['trains'].append(new_train_data)
    result['updates'] = []
    for u in train_data['updates']:
        result['updates'].append({'link': u['link'],
                                  'text': jinja2.Markup(u['text']).unescape()})
    return result


def get_train_data(station_from, station_to):
    url = "http://ojp.nationalrail.co.uk/en/s/ldb/liveTrainsJson?departing=true&liveTrainsFrom={station_from}&liveTrainsTo={station_to}&serviceId=&f="
    url = url.format(station_from=station_from, station_to=station_to)
    r = requests.get(url)
    return r.json()


def macro_NatRailLiveDepartures(macro, station_from, station_to):
    result = '<strong>Data cannot be retrieved</strong>'

    train_data = get_train_data(station_from, station_to)
    if train_data:
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))
        tpl = env.get_template("NatRailLiveDepartures.html")
        train_data = cleanup_data(train_data) # this must go first as it copies each individual element of an array
        train_data = add_time_at_destination(train_data, station_to)
        result = tpl.render(train_data=train_data)

    return result



def test():
    r = macro_NatRailLiveDepartures(None, 'WIM', 'KNG')
    print(r)


if __name__ == '__main__':
    test()

