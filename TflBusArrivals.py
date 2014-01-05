# -*- coding: utf-8 -*-
"""
    MoinMoin - TFL Live Bus Arrivals
"""

import os
import re
import json
import time
import datetime
import operator
import requests
import jinja2


def get_data(stop_id, filters={}):

    req_fields = [ 'StopPointName', 
                   'StopID',
                   'StopCode1',
                   'StopCode2',
                   'StopPointState',
                   'StopPointType',
                   'StopPointIndicator', 
                   'Towards',
                   'Bearing',
                   'Latitude',
                   'Longitude',
                   'VisitNumber',
                   'TripID',
                   'VehicleID',
                   'RegistrationNumber',
                   'LineID',
                   'LineName',
                   'DirectionID',
                   'DestinationText',
                   'DestinationName',
                   'EstimatedTime', 
                   'MessageUUID',
                   'MessageText',
                   'MessageType',
                   'MessagePriority', 
                   'StartTime',
                   'ExpireTime',
                   'BaseVersion' ]

    result = None

    url_tpl = 'http://countdown.api.tfl.gov.uk/interfaces/ura/instant_V1?StopCode1={stop_id}&ReturnList={fields}'
    url = url_tpl.format(stop_id=stop_id, fields=','.join(req_fields))
    for f in filters.iteritems():
        url += '&{filter_key}={filter_val}'.format(filter_key=f[0], filter_val=f[1])

    try:
        r = requests.get(url)
        result = r.text
    except requests.exceptions.ConnectionError:
        pass

    return result


def parse_raw_data(raw_tfl_data):
    message_lines = re.split('\n+', raw_tfl_data)
    messages = map(json.loads, message_lines[1:])  # skip first message as it is just a version string
    return messages


def format_time(epoch_ts, format='%H:%M'):
    return time.strftime('%H:%M', time.localtime(epoch_ts / 1000.0))


def get_wait_time(estimated_time):
    current_time = time.time()
    delta_sec = int(estimated_time / 1000 - current_time)
    return delta_sec / 60


def extract_prediction_messages(messages):
    result = []
    for m in messages:
        if m[0] != 1:   # prediction messages have type 1
            continue
        result.append( {'StopPointName': m[1],
                        'StopID': m[2],
                        'StopCode1': m[3],
                        'StopCode2': m[4],
                        'StopPointType': m[5],
                        'Towards': m[6],
                        'Bearing': m[7],
                        'StopPointIndicator': m[8],
                        'StopPointState': m[9],
                        'Latitude': m[10],
                        'Longitude': m[11],
                        'VisitNumber': m[12],
                        'LineID': m[13],
                        'LineName': m[14],
                        'DirectionID': m[15],
                        'DestinationText': m[16],
                        'DestinationName': m[17],
                        'VehicleID': m[18],
                        'TripID': m[19],
                        'RegistrationNumber': m[20],
                        'EstimatedTime': format_time(m[21]),
                        'ExpireTime': format_time(m[22]),
                        'estimated_wait_time': get_wait_time(m[21]), })
    return result

def extract_service_messages(messages):
    result = []
    for m in messages:
        if m[0] != 2:   # service messages have type 2
            continue
        result.append( {'StopPointName': m[1],
                        'StopID': m[2],
                        'StopCode1': m[3],
                        'StopCode2': m[4],
                        'StopPointType': m[5],
                        'Towards': m[6],
                        'Bearing': m[7],
                        'StopPointIndicator': m[8],
                        'StopPointState': m[9],
                        'Latitude': m[10],
                        'Longitude': m[11],
                        'MessageUUID': m[12],
                        'MessageType': m[13],
                        'MessagePriority': m[14],
                        'MessageText': m[15],
                        'StartTime': m[16],
                        'ExpireTime': m[17], })
    return result


def macro_TflBusArrivals(macro, bus_stop_code, line_ids=None):
    """
    Macro to display live bus arrivals
    """

    result = '<strong>Data cannot be retrieved</strong>'
    filters = {}

    if line_ids:
        filters['LineID'] = line_ids

    raw_data = get_data(bus_stop_code, filters)
    if raw_data:
        messages = parse_raw_data(raw_data)
        pm = sorted(extract_prediction_messages(messages), key=operator.itemgetter('estimated_wait_time'))
        sm = extract_service_messages(messages)
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))
        tpl = env.get_template("TflBusArrivals.html")
        result = tpl.render(prediction_messages=pm,
                            service_messages=sm)

    return result

