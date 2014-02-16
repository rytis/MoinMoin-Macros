#!/usr/bin/python
#
# Note:
#  You need to create a config file called `config/MetOfficeDaily.ini` with the following in it:
#
#  [api]
#  key=<MET office API key>
#
# Register you account for free at:
#   https://register.metoffice.gov.uk/WaveRegistrationClient/public/newaccount.do?service=datapoint
# Once registered you will be provided with an API key (for free at the time of writing)
#

import os
import pprint
from collections import namedtuple
import requests
import jinja2


WEATHER_TYPE = {
    '0': 'Clear night',
    '1': 'Sunny day',
    '2': 'Partly cloudy',
    '3': 'Partly cloudy',
    '4': 'Not used',
    '5': 'Mist',
    '6': 'Fog',
    '7': 'Cloudy',
    '8': 'Overcast',
    '9': 'Light rain shower',
    '10': 'Light rain shower',
    '11': 'Drizzle',
    '12': 'Light rain',
    '13': 'Heavy rain shower',
    '14': 'Heavy rain shower',
    '15': 'Heavy rain',
    '16': 'Sleet shower',
    '17': 'Sleet shower',
    '18': 'Sleet',
    '19': 'Hail shower',
    '20': 'Hail shower',
    '21': 'Hail',
    '22': 'Light snow shower',
    '23': 'Light snow shower',
    '24': 'Light snow',
    '25': 'Heavy snow shower',
    '26': 'Heavy snow shower',
    '27': 'Heavy snow',
    '28': 'Thunder shower',
    '29': 'Thunder shower',
    '30': 'Thunder',
}


DailyForecastRecord = namedtuple("DailyForecastRecord", ["part_of_day",
                                                         "feels_like_temp",
                                                         "temp",
                                                         "precip_probability",
                                                         "weather_type",
                                                         "weather_type_id",
                                                         "wind_speed",
                                                         "wind_gust"])

DailyForecast = namedtuple("DailyForecast", ["date", "data"])

def get_multi_key(d, kl, default=None):
    for k in kl:
        if k in d.keys():
            return d[k]
    return default

def extract_5day_data(full_site_data):
    result = []
    for day_data in full_site_data['SiteRep']['DV']['Location']['Period']:
        rec = DailyForecast(date=day_data['value'][:-1], data=[])
        for i in range(2):
            data = DailyForecastRecord(part_of_day=day_data['Rep'][i]['$'],
                                       feels_like_temp=get_multi_key(day_data['Rep'][i], ['FDm', 'FNm']),
                                       temp=get_multi_key(day_data['Rep'][i], ['Dm', 'Nm']),
                                       precip_probability=get_multi_key(day_data['Rep'][i], ['PPd', 'PPn']),
                                       weather_type=WEATHER_TYPE[day_data['Rep'][i]['W']],
                                       weather_type_id=day_data['Rep'][i]['W'],
                                       wind_gust=int(get_multi_key(day_data['Rep'][i], ['Gn', 'Gm'])) * 1.6,
                                       wind_speed=int(day_data['Rep'][i]['S']) * 1.6)
            rec.data.append(data)
        result.append(rec)
    return result


def macro_MetOfficeDaily(macro, location_id):
    result = '<strong>Data cannot be retrieved</strong>'
    url = "http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/{location_id}?res=daily&key={api_key}".format(api_key="a8d427d6-10da-4c5c-946e-a873c443fc76", location_id=location_id)
    r = requests.get(url)
    five_day_data = extract_5day_data(r.json())

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))
    tpl = env.get_template("MetOfficeDaily.html")
    result = tpl.render(forecast_data=five_day_data)

    return result


if __name__ == '__main__':
    #pprint.pprint(macro_MetOfficeDaily(None, 3080))
    print(macro_MetOfficeDaily(None, 3080))

# 'Feels Like Day Maximum Temperature'
# 'name': u'FDm'
# 'units': u'C'
# 'Feels Like Night Minimum Temperature'
# 'name': u'FNm'
# 'units': u'C'
# 'Day Maximum Temperature'
# 'name': u'Dm'
# 'units': u'C'
# 'Night Minimum Temperature'
# 'name': u'Nm'
# 'units': u'C'
# 'Wind Gust Noon'
# 'name': u'Gn'
# 'units': u'mph'
# 'Wind Gust Midnight'
# 'name': u'Gm'
# 'units': u'mph'
# 'Screen Relative Humidity Noon'
# 'name': u'Hn'
# 'units': u'%'
# 'Screen Relative Humidity Midnight'
# 'name': u'Hm'
# 'units': u'%'
# 'Visibility'
# 'name': u'V'
# 'units': u''
# 'Wind Direction'
# 'name': u'D'
# 'units': u'compass'
# 'Wind Speed'
# 'name': u'S'
# 'units': u'mph'
# 'Max UV Index'
# 'name': u'U'
# 'units': u''
# 'Weather Type'
# 'name': u'W'
# 'units': u''
# 'Precipitation Probability Day'
# 'name': u'PPd'
# 'units': u'%'
# 'Precipitation Probability Night'
# 'name': u'PPn'
# 'units': u'%'

