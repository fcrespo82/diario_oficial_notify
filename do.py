#!/usr/bin/env python
from collections import namedtuple
from socket import if_nameindex
from typing import NamedTuple
import requests
import datetime
from bs4 import BeautifulSoup
import logging
import argparse
import re
import os

API_KEY = os.getenv('API_KEY')
USER_KEY = os.getenv('USER_KEY')

PushoverData = namedtuple('PushoverData', ['message', 'url', 'url_title'])


def debug2(obj):
    if args.debug >= 2:
        logging.debug(obj)


def my_regex_type(arg_value, pat=re.compile(r"^\d{2}/\d{2}/\d{4}$")):
    try:
        parsed_date = datetime.datetime.strptime(arg_value, '%d/%m/%Y')
    except:
        raise argparse.ArgumentTypeError(
            f'\'{arg_value}\' deve ser uma data válida (formato dd/mm/aaaa)')
    return parsed_date


def setup_argparse():
    parser = argparse.ArgumentParser(
        description='busca diario oficial pelos parametros informados')
    parser.add_argument('-d', '--debug', action='count', default=0,
                        help="Aumenta verbosidade, suporta múltiplos usos")
    parser.add_argument('palavra_chave')
    g1 = parser.add_argument_group()
    g1.add_argument('--inicio', type=my_regex_type,
                    help='Data inicial (formato: dd/mm/aaaa)')
    g1.add_argument('--fim', type=my_regex_type,
                    help='Data final (formato: dd/mm/aaaa)')

    g2 = parser.add_argument_group()
    g2.add_argument('--data', type=my_regex_type,
                    help='Data (formato: dd/mm/aaaa)')

    return parser


def searchBetween(txt_for, date_from=datetime.datetime.now(), date_to=datetime.datetime.now()):
    palavra_chave = f'{txt_for}'
    periodo = f'{date_from.strftime("%d/%m/%Y")}+a+{date_to.strftime("%d/%m/%Y")}'

    url = f'http://www.imprensaoficial.com.br/DO/BuscaDO2001Resultado_11_3.aspx?filtropalavraschave={palavra_chave}&filtrogrupos=Legislativo+&filtroperiodo={periodo}&filtrotodosgrupos=False&CampoOrdenacao=datapublicacao&DirecaoOrdenacao=descending'

    logging.debug(url)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, features='html5lib')
    mensagem = soup.find(id='content_lblMensagem')
    debug2(soup.prettify())
    if mensagem:
        logging.warning('No data found')
        return []
    else:
        results = soup.find_all('div', {'class': 'resultadoBuscaItem'})
        debug2(results)
        logging.debug(f'Found {len(results)} results')

        objs = map(extract_info, results)

        return list(objs)


def extract_info(result):
    title = result.find('span', {'class': 'card-title'})
    logging.info(title.text)
    card_text = result.find('p', {'class': 'card-text'})
    logging.debug(card_text)
    link = card_text.find('a')
    logging.debug(link)
    url = f'http://www.imprensaoficial.com.br/{link["href"]}'
    logging.info(url)
    text = link.text.strip()
    logging.info(text)

    return PushoverData(url_title=title.text, url=url, message=text)


def searchDay(txt_for, date=datetime.datetime.now()):
    return searchBetween(txt_for, date, date)


def send_notification(pushover_data):
    result = requests.post('https://api.pushover.net/1/messages.json', {
        'token': API_KEY,
        'user': USER_KEY,
        'message': pushover_data.message,
        'url': pushover_data.url,
        'url_title': pushover_data.url_title,
    })
    logging.debug(result)


def custom_parse(parser, args):
    if not (args.inicio or args.fim or args.data):
        print(f'{parser.prog}: error: either (argument --inicio and --fim) or (argument --data) are required')
        exit(1)
    elif (args.inicio or args.fim):
        if (args.inicio) and args.data:
            print(
                f'{parser.prog}: error: argument --inicio: not allowed with argument --data')
            exit(1)
        elif (args.fim) and args.data:
            print(
                f'{parser.prog}: error: argument --fim: not allowed with argument --data')
            exit(1)
        elif not (args.inicio and args.fim):
            print(
                f'{parser.prog}: error: argument --inicio and argument --fim are required.')
            exit(1)


def parse_env():
    if not (API_KEY or USER_KEY):
        print("Missing environment variables")
        exit(1)

parser = setup_argparse()
args = parser.parse_args()
custom_parse(parser, args)
parse_env()

if __name__ == '__main__':
    level = logging.DEBUG if args.debug else logging.WARNING
    logging.basicConfig(level=level)
    if args.data:
        items = searchDay(args.palavra_chave, args.data)
    else:
        items = searchBetween(args.palavra_chave, args.inicio, args.fim)

    # print(args)
    for item in items:
        send_notification(item)
