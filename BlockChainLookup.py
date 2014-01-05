#!/usr/bin/env python

import os
import json
import time
import pprint
import jinja2
import requests


BTC_MULTIPLIER = 100000000.00


def get_exchange_rate(currency='GBP'):
    url = "http://blockchain.info/ticker"
    r = requests.get(url)
    if currency in r.json():
        return r.json()[currency]['15m']
    else:
        return r.json()['GBP']['15m']


def get_address_data(address):
    url = "http://blockchain.info/address/{address}?format=json".format(address=address)
    r = requests.get(url)
    return r.json()


def extract_address_details(bc_data, exch_rate):
    result = { 'address': bc_data['address'],
               'balance': bc_data['final_balance'] / BTC_MULTIPLIER,
               'balance_exch': exch_rate * bc_data['final_balance'] / BTC_MULTIPLIER,
               'transactions': [] }
    if bc_data['txs']:
        for tx in bc_data['txs']:
            tx_is_credit = False  # credit - btc spent, debit - btc received
            value = 0
            for inp in tx['inputs']:
                # check if we sent any coins
                if inp['prev_out']['addr'] == bc_data['address']:
                    tx_is_credit = True
                    value -= inp['prev_out']['value']
            for out in tx['out']:
                if out['addr'] == bc_data['address']:
                    # we also might have sent part of it to ourself
                    value += out['value']
            tx_data = { 'value': value / BTC_MULTIPLIER,
                        'value_exch': exch_rate * value / BTC_MULTIPLIER,
                        'date': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tx.get('time', 0))) }
            result['transactions'].append(tx_data)
    return result


def macro_BlockChainLookup(macro, address, currency='GBP'):
    result = '<strong>Data cannot be retrieved</strong>'

    bc_data = get_address_data(address)
    exch_rate = get_exchange_rate(currency)
    addr_info = extract_address_details(bc_data, exch_rate)

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))
    tpl = env.get_template("BlockChainLookup.html")
    result = tpl.render(addr_info=addr_info)

    return result


def test():
    result = macro_BlockChainLookup(None, '1C8hhHSycVnH1TUhALPX8PSrQDWTTJ7HuF')
    print(result)


if __name__ == '__main__':
    test()

