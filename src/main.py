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


def br_date_type(str_date):
    '''
    Valida se a data está no formato dd/mm/aaaa
    '''
    try:
        parsed_date = datetime.datetime.strptime(str_date, '%d/%m/%Y')
    except Exception as ex:
        raise argparse.ArgumentTypeError(
            f'\'{str_date}\' deve ser uma data válida (formato dd/mm/aaaa)') from ex
    return parsed_date


def setup_argparse():
    '''
    Configura o parser de argumentos
    '''
    parser = argparse.ArgumentParser(
        description='busca diario oficial pelos parametros informados')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')

    parser.add_argument('palavra_chave')
    parser.add_argument('--pushover', action='store_true', default=False,
                        help="Envia mensagem através do serviço Pushover")
    group_one = parser.add_argument_group()
    group_one.add_argument('--inicio', type=br_date_type,
                           help='Data inicial (formato: dd/mm/aaaa)')
    group_one.add_argument('--fim', type=br_date_type,
                           help='Data final (formato: dd/mm/aaaa)')

    group_two = parser.add_argument_group()
    group_two.add_argument('--data', type=br_date_type,
                           help='Data (formato: dd/mm/aaaa)')

    return parser


def verify_args(parser, args):
    '''
    Verifica se os argumentos são válidos
    '''
    if not (args.inicio or args.fim or args.data):
        print(f'{parser.prog}: error: either (argument --inicio and --fim) \
or (argument --data) are required')
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


def main():
    parser = setup_argparse()
    args = parser.parse_args()
    log = logging.getLogger()
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    if args.debug:
        log.setLevel(logging.DEBUG)
    elif args.verbose:
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.WARNING)

    verify_args(parser, args)
    logging.debug(args)

    diario_oficial = DiarioOficial()
    if args.data:
        items = diario_oficial.busca_dia(args.palavra_chave, args.data)
    else:
        items = diario_oficial.busca_entre_datas(
            args.palavra_chave, args.inicio, args.fim)

    api_key = os.getenv('PUSHOVER_API_KEY')
    user_key = os.getenv('PUSHOVER_USER_KEY')

    pushover = Pushover(user_key, api_key)

    for message, url, url_title in items:
        if args.pushover:
            pushover.notify(message, url, url_title)


if __name__ == '__main__':
    main()
