#!/usr/bin/python3
import json
from decimal import Decimal

import requests


class OneInchSwapUSDT(object):
    """1inch聚合交易所"""

    base_url = 'https://api.1inch.exchange'

    chains = dict(
        ethereum='1',
        binance='56'
    )

    version = "v4.0"

    endpoints = dict(
        quote="quote",
        swap="swap",
        tokens="tokens",
        protocols="protocols",
        protocols_images="protocols/images",
        approve_spender="approve/spender",
        approve_transaction="approve/transaction",
        approve_allowance="approve/allowance"
    )

    tokens = dict()
    tokens_by_address = dict()
    protocols = []
    protocols_images = []

    def __init__(self, address, chain='ethereum'):
        self.address = address
        self.chain_id = self.chains[chain]
        self.chain = chain
        # self.get_tokens()
        # self.get_protocols()
        # self.get_protocols_images()

    def _get(self, url, params=None, headers=None):
        """ Implements a get request """
        try:
            response = requests.get(url, params=params, headers=headers)
            payload = json.loads(response.text)
            data = payload
        except requests.exceptions.ConnectionError as e:
            print("ConnectionError when doing a GET request from {}".format(url))
            data = None
        return data

    def health_check(self):
        url = '{}/{}/{}/healthcheck'.format(self.base_url, self.version, self.chain_id)
        response = requests.get(url)
        result = json.loads(response.text)
        if not result.__contains__('statusCode'):
            return result
        return result['description']

    def get_tokens(self):
        url = '{}/{}/{}/tokens'.format(self.base_url, self.version, self.chain_id)
        result = self._get(url)
        if not result.__contains__('tokens'):
            return result
        for address in result['tokens']:
            token = result['tokens'][address]
            self.tokens_by_address[address] = token
            self.tokens[token['symbol']] = token
        return self.tokens

    def get_protocols(self):
        url = '{}/{}/{}/protocols'.format(self.base_url, self.version, self.chain_id)
        result = self._get(url)
        if not result.__contains__('protocols'):
            return result
        self.protocols = result
        return self.protocols

    def get_protocols_images(self):
        url = '{}/{}/{}/protocols/images'.format(self.base_url, self.version, self.chain_id)
        result = self._get(url)
        if not result.__contains__('protocols'):
            return result
        self.protocols_images = result
        return self.protocols_images

    def get_quote(self, from_token_symbol: str, to_token_symbol: str, amount: int):
        url = '{}/{}/{}/quote'.format(self.base_url, self.version, self.chain_id)
        url = url + '?fromTokenAddress={}&toTokenAddress={}&amount={}'.format(
            self.tokens[from_token_symbol]['address'],
            self.tokens[to_token_symbol]['address'],
            format(Decimal(10 ** self.tokens[from_token_symbol]['decimals'] * amount).quantize(Decimal('1.')), 'n'))
        result = self._get(url)
        return result

    def do_swap(self, from_token_symbol: str, to_token_symbol: str, amount: int, from_address: str, slippage: int):
        url = '{}/{}/{}/swap'.format(self.base_url, self.version, self.chain_id)
        url = url + "?fromTokenAddress={}&toTokenAddress={}&amount={}".format(
            self.tokens[from_token_symbol]['address'],
            self.tokens[to_token_symbol]['address'],
            amount)
        url = url + '&fromAddress={}&slippage={}'.format(from_address, slippage)
        result = self._get(url)
        return result

    def convert_amount_to_decimal(self, token_symbol, amount):
        decimal = self.tokens[token_symbol]['decimals']
        return Decimal(amount) / Decimal(10 ** decimal)
