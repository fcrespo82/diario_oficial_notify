'''
Realiza buscas no diário oficial
'''

import datetime
import logging
import requests
from bs4 import BeautifulSoup

__all__ = ['DiarioOficial']


class DiarioOficial:
    '''
    Gerenciar as pesquisas no diário oficial
    '''

    def __init__(self):
        self.log = logging.getLogger(__name__)

    def busca_entre_datas(self,
                          txt_for,
                          date_from=datetime.datetime.now(),
                          date_to=datetime.datetime.now()):
        '''
        Busca o texto no diário oficial entre duas datas
        '''
        palavra_chave = f'{txt_for}'
        periodo = f'{date_from.strftime("%d/%m/%Y")}+a+{date_to.strftime("%d/%m/%Y")}'

        url = f'http://www.imprensaoficial.com.br/DO/BuscaDO2001Resultado_11_3.aspx?\
filtropalavraschave={palavra_chave}&\
filtroperiodo={periodo}&\
filtrogrupos=Legislativo+&\
filtrotodosgrupos=False&\
CampoOrdenacao=datapublicacao&\
DirecaoOrdenacao=descending'

        self.log.debug(url)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, features='html5lib')
        mensagem = soup.find(id='content_lblMensagem')
        self.log.debug(soup.prettify())
        if mensagem:
            self.log.warning('No data found')
            return []
        else:
            results = soup.find_all('div', {'class': 'resultadoBuscaItem'})
            self.log.debug(results)
            self.log.debug('Found %s results', results)

            objs = map(self._extract_info, results)

            return list(objs)

    def _extract_info(self, result):
        '''
        Extrai informações do resultado da busca
        '''
        title = result.find('span', {'class': 'card-title'})
        self.log.info(title.text)
        card_text = result.find('p', {'class': 'card-text'})
        self.log.debug(card_text)
        link = card_text.find('a')
        self.log.debug(link)
        url = f'http://www.imprensaoficial.com.br/{link["href"]}'
        self.log.info(url)
        text = link.text.strip()
        self.log.info(text)

        return (text, url, title.text)

    def busca_dia(self, txt_for, date=datetime.datetime.now()):
        '''
        Busca o texto no diário oficial para um dia específico
        '''
        return self.busca_entre_datas(txt_for, date, date)
