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

    date_group = parser.add_argument_group('Data de busca')

    data_mutex_group = date_group.add_mutually_exclusive_group(required=True)
    data_mutex_group.add_argument('--periodo', nargs=2, metavar=('INICIO', 'FIM'),
                                  type=br_date_type, help='Período para busca entre INICIO e FIM (formato das datas: dd/mm/aaaa)')
    data_mutex_group.add_argument('--data', type=br_date_type,
                                  help='Data para busca (formato: dd/mm/aaaa)')

    pushover_group = parser.add_argument_group('Pushover')

    pushover_group.add_argument('--pushover_user',
                                help="User Key para envio de notificação através do serviço Pushover")
    pushover_group.add_argument('--pushover_api',
                                help="Api Key para envio de notificação através do serviço Pushover")

    # email_group = parser.add_argument_group('E-mail')

    # email_group.add_argument('--email-smtp',
    #                          help="SMTP server para envio de notificação através de e-mail")
    # email_group.add_argument('--email-from',
    #                          help="E-mail 'DE' para envio de notificação através de e-mail")

    return parser


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

    logging.info(args)

    diario_oficial = DiarioOficial()
    if args.data:
        items = diario_oficial.busca_dia(args.palavra_chave, args.data)
    else:
        items = diario_oficial.busca_entre_datas(
            args.palavra_chave, args.periodo[0], args.periodo[1])

    if args.pushover_user and args.pushover_api:
        pushover = Pushover(args.pushover_user, args.pushover_api)
        for message, url, url_title in items:
            pushover.notify(message, url, url_title)


if __name__ == '__main__':
    main()
