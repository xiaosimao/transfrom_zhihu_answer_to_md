#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by shimeng on 17-5-25



import requests


def get_random_proxy():
    try:
        # 远程主机的服务地址
        url = 'http://139.217.26.30/random'
        return requests.get(url).text
    except requests.exceptions.ConnectionError:
        return None


if __name__ == '__main__':
    print get_random_proxy()