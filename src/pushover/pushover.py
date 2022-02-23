'''
Envia notificações através do Pushover
'''

import logging
import requests

__all__ = ['Pushover']


class MissingArgumentError(ValueError):
    'MissingArgumentError'


class Pushover:
    '''
    Gerencia o envio de notificações através do Pushover
    '''
    API_URL = 'https://api.pushover.net/1/messages.json'

    def __init__(self, user_token, api_token) -> None:
        self.log = logging.getLogger(__name__)
        self.user_token = user_token
        self.api_token = api_token

    def notify(self, message, url, url_title):
        '''
        Envia notificação através do Pushover
        '''
        if not message:
            raise MissingArgumentError('message is required')
        data = {
            'token': self.api_token,
            'user': self.user_token,
            'message': message
        }

        if url:
            data['url'] = url
        if url_title:
            data['url_title'] = url_title

        result = requests.post(self.API_URL, data=data)
        self.log.debug(result.text)

        if result.status_code != 200:
            new_line = '\n'
            raise RuntimeError(
                f'''Error sending message to Pushover:
Token: '{self.api_token}'
User: '{self.user_token}'
Status code: {result.status_code}
Error: {new_line.join(result.json()["errors"])}''')


if __name__ == '__main__':
    p = Pushover('user_token', 'api_token')
    p.notify('a', 'url', 'url_title')
