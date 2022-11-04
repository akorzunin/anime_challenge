import pandas as pd
from pandas.core.frame import DataFrame
from shikimori_api import Shikimori
import plotly.express as px
import json
import requests
import bs4

import os
from dotenv import load_dotenv
load_dotenv()

from member_list import members

class ShikiDs(object): 
    '''docstring for ClassName'''
    def __init__(self, **kwargs):
        super(ShikiDs, self).__init__()
        self.token = None,
        self.TOKEN_PATH = kwargs.pop('TOKEN_PATH',)
        self.read_token()

    def read_token(self):
        with open(self.TOKEN_PATH) as f:
            token = json.load(f)
        self.token =  token['access_token']
        # add more information from token file later
        return token

    def get_data(self, username: str=None, category: str=None, save_data: bool=False, filter_by_type: list=None) -> DataFrame:
        '''category: 'planned', 'watching,rewatching', 'completed', 'on_hold', 'dropped';
            filter_rows: 'Сериал', 'Фильм', 'ONA', 'OVA'
        '''
        def anime_headers(token = ""):
            headers = {"User-Agent": "application", "Content-Type": "application/json"}
            if self.token:
                headers["Authorization"] = f"Bearer {token}"
            return headers
        avalible_states= (
            'planned', 
            'watching,rewatching',
            'completed',
            'on_hold',
            'dropped',
        )
        if category in avalible_states: 
            title_state = category
        else: return 'category not avalible'
        r = requests.get(url=f'https://shikimori.one/{username}/list/anime/mylist/{title_state}/order-by/rate_score', 
            headers=anime_headers(self.token)) 
        if r.status_code == 200:
            if save_data:   
                filename = f'./cashed_html/{username}_{title_state}.html'
                with open(filename, 'w+', encoding='utf-8') as f:
                    f.write(r.text)

            # handle response w/ bs4 parser == "lxml"
            soup = bs4.BeautifulSoup(r.text, features="lxml")
            self_user = ' editable' if username == 'Elaeagnus' else ''
            content = soup.find_all("tr", {"class": f"user_rate unprocessed selectable{self_user}"})
            # check if page not empty
            try:
                content[0]
            except IndexError: return 'category empty'
            df = self.extract_data(filter_by_type, content)
            return df
        else: return pd.DataFrame()

    def extract_data(self, filter_by_type, content):
        data_list = []
        for el in content:
            id = el.attrs['data-target_id']
            try:
                name_en = el.find_all('a', {'class': 'tooltipped'})[0].find_all(lambda tag: tag.name == "span")[0].text
            except IndexError: name_en = 'N/A'
            try:
                name_ru = el.find_all('a', {'class': 'tooltipped'})[0].find_all(lambda tag: tag.name == "span")[1].text
            except IndexError: name_ru = 'N/A'
            user_rate = el.find('span', {'data-field': 'score'}).text
            ep_current = el.find('span', {'data-field': 'episodes'}).text
            ep_max = el.find('span', {'class': 'misc-value'}).text
            title_type = el.find_all('td')[-1].text
            data_list.append(
                    {
                        'id': id,
                        'name_en': name_en,
                        'name_ru': name_ru,
                        'user_rate': user_rate,
                        'ep_current': ep_current,
                        'ep_max': ep_max,
                        'title_type': title_type,
                    }
                )
            df = pd.DataFrame(data_list)
            if filter_by_type is not None:
                    # left only filtered rows
                    # df = df.loc[df['title_type'] in filter_by_type] deprecated
                df = df.query(f"title_type in {filter_by_type}")
        return df


if __name__ == '__main__':
    a = ShikiDs(
        TOKEN_PATH='./token.json'
        )
    df = a.get_data(
        username='zorome666',
        category='dropped'

    )
    print( type(df), df)