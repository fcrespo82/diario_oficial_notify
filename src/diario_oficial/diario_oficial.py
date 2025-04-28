'''
Realiza buscas no diário oficial
'''

import datetime
import logging
import json
from typing import Any
import urllib.parse
import requests

from .result import Result

__all__: list[str] = ['DiarioOficial']


class DiarioOficial:
    '''
    Gerenciar as pesquisas no diário oficial
    '''

    def __init__(self):
        self.log = logging.getLogger(__name__)

    def busca_entre_datas(self,
                          txt_keyword: str,
                          date_from: datetime.datetime=datetime.datetime.now(),
                          date_to: datetime.datetime=datetime.datetime.now())->list[Result]:
        '''
        Busca o texto no diário oficial entre duas datas
        '''
        txt_keyword_quoted = f'"{txt_keyword}"'
        palavra_chave = urllib.parse.quote_plus(txt_keyword_quoted)

        print(f'Buscando por {txt_keyword_quoted} de {date_from.strftime("%d/%m/%Y")} até {date_to.strftime("%d/%m/%Y")}')
        url = f'https://do-api-web-search.doe.sp.gov.br/v2/advanced-search/publications?\
periodStartingDate={date_from.strftime("%Y-%m-%d")}&\
FromDate={date_from.strftime("%Y-%m-%d")}&\
ToDate={date_to.strftime("%Y-%m-%d")}&\
JournalId=0953858b-7195-4020-ec15-08db6b8e0e4c&\
Terms%5B0%5D={palavra_chave}'

        self.log.debug(url)
        response = requests.get(url, timeout=60)

        response_json = json.loads(response.text)

        results = response_json["items"]

        self.log.debug(results)
        print(
            f'Encontrado {len(results)} resultado{"s" if len(results) > 1 else ""}')

        objs = list(map(self._extract_info_from_json, results))

        objs = list(map(self._set_title, objs, [txt_keyword]*len(objs)))

        self.log.info(objs)
        return objs

    def _set_title(self, result: Result, txt_keyword: str):
        result.title = txt_keyword
        return result
    
    def _extract_info(self, result: Any):
        '''
        Extrai informações do resultado da busca
        '''
        title = result.find_next('span', {'class': 'card-title'})
        self.log.info(title.text)
        card_text = result.find_next('p', {'class': 'card-text'})
        self.log.debug(card_text)
        link = card_text.find_next('a')
        self.log.debug(link)
        url = f'http://www.imprensaoficial.com.br{link["href"]}'
        # Substitui link para abrir o PDF direto e não em um IFRAME
        url = url.replace(
            'BuscaDO2001Documento_11_4.aspx', 'GatewayPDF.aspx')
        self.log.info(url)
        text = link.text.strip()
        self.log.info(text)

        self.log.info(json.dumps((text, url, title.text), indent=4))
        return Result(text, url, title.text)

    def _extract_info_from_json(self, result: dict):
        '''
        Extrai informações do resultado da busca
        '''
        title = result['title']
        self.log.info(title)
        link = result['slug']
        self.log.debug(link)
        url = f'https://do-api-web-search.doe.sp.gov.br/{link}'
        self.log.info(url)
        text = result['excerpt']
        self.log.info(text)

        self.log.info(json.dumps((text, url, title), indent=4))
        return Result(text, url, title)
    
    def busca_dia(self, txt_keyword: str, date:datetime.datetime=datetime.datetime.now()):
        '''
        Busca o texto no diário oficial para um dia específico
        '''
        return self.busca_entre_datas(txt_keyword, date, date)
