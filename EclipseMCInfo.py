#!/usr/bin/env python

import os
import json
import time
import pprint
import jinja2
import requests


def get_emc_account_info(api_key):
    url = "https://eclipsemc.com/api.php?key={key}&action=userstats".format(key=api_key)
    r = requests.get(url, verify=False)
    return r.json()


def macro_EclipseMCInfo(macro, api_key):
    result = '<strong>Data cannot be retrieved</strong>'

    status = get_emc_account_info(api_key)

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))
    tpl = env.get_template("EclipseMCInfo.html")
    result = tpl.render(status=status)

    return result



def test():
    result = macro_EclipseMCInfo(None, 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    print(result)


if __name__ == '__main__':
    test()
