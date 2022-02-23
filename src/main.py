#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
CLI para busca e notificação do Diário Oficial
'''
import datetime
import logging
import argparse
import os
from pushover import Pushover
from diario_oficial import DiarioOficial


def br_date_type(arg_value):
    'Converte a data para o formato brasileiro'
    try:
        parsed_date = datetime.datetime.strptime(arg_value, '%d/%m/%Y')
    except Exception as ex:
        raise argparse.ArgumentTypeError(
            f'\'{arg_value}\' deve ser uma data válida (formato dd/mm/aaaa)') from ex
    return parsed_date


def setup_argparse():
    '''
    Configura o parser de argumentos
    '''
    _parser = argparse.ArgumentParser(
        description='busca diario oficial pelos parametros informados')
    _parser.add_argument('-d', '--debug', action='count', default=0,
                         help="Aumenta verbosidade, suporta múltiplos usos")
    _parser.add_argument('palavra_chave')
    _parser.add_argument('--pushover', action='store_true', default=False,
                         help="Envia mensagem através do serviço Pushover")
    group_one = _parser.add_argument_group()
    group_one.add_argument('--inicio', type=br_date_type,
                           help='Data inicial (formato: dd/mm/aaaa)')
    group_one.add_argument('--fim', type=br_date_type,
                           help='Data final (formato: dd/mm/aaaa)')

    group_two = _parser.add_argument_group()
    group_two.add_argument('--data', type=br_date_type,
                           help='Data (formato: dd/mm/aaaa)')

    return _parser


def verify_args(_parser, _args):
    '''
    Verifica se os argumentos são válidos
    '''
    if not (_args.inicio or _args.fim or _args.data):
        print(f'{_parser.prog}: error: either (argument --inicio and --fim) \
or (argument --data) are required')
        exit(1)
    elif (_args.inicio or _args.fim):
        if (_args.inicio) and _args.data:
            print(
                f'{_parser.prog}: error: argument --inicio: not allowed with argument --data')
            exit(1)
        elif (_args.fim) and _args.data:
            print(
                f'{_parser.prog}: error: argument --fim: not allowed with argument --data')
            exit(1)
        elif not (_args.inicio and _args.fim):
            print(
                f'{_parser.prog}: error: argument --inicio and argument --fim are required.')
            exit(1)


if __name__ == '__main__':
    parser = setup_argparse()
    args = parser.parse_args()
    LOG_LEVEL = logging.DEBUG if args.debug else logging.WARNING
    logging.basicConfig(level=LOG_LEVEL,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    verify_args(parser, args)
    logging.debug(args)

    do = DiarioOficial()
    if args.data:
        items = do.busca_dia(args.palavra_chave, args.data)
    else:
        items = do.busca_entre_datas(args.palavra_chave, args.inicio, args.fim)

    API_KEY = os.getenv('PUSHOVER_API_KEY')
    USER_KEY = os.getenv('PUSHOVER_USER_KEY')

    p = Pushover(API_KEY, USER_KEY)

    for message, url, url_title in items:
        if args.pushover:
            p.notify(message, url, url_title)
