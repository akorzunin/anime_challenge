
import time
import pandas as pd
from pandas.core.frame import DataFrame
from shikimori_api import Shikimori
import plotly.express as px
import json

import os
from dotenv import load_dotenv
load_dotenv()

class ShiNoAuth(object): 
    '''docstring for ClassName'''
    def __init__(self, *arg):
        super(ShiNoAuth, self).__init__()
        self.init_api()

    def init_api(self):
        session = Shikimori()
        self.api = session.get_api()
        return self.api

    def convert_to_dict(self, label: str, stats, append=None) -> dict:
        tempo = [list(i.values()) for i in stats[label]['anime']]
        append = append if append is not None else ''
        return {i[0]+f'{append}': i[1] for i in tempo}

    # decorator to convert dict to df w/ custom names
    def to_df(col_one, col_two):
        def dec(func, ):
            def wrapper(*args, **kwargs):
                in_dict = func(*args, **kwargs)
                return pd.DataFrame(data={
                    col_one: list(in_dict.keys()),
                    col_two: in_dict.values(),
                })
            return wrapper
        return dec


    def get_df_w_ptw(self, member):
        
        r = self.api.users(member).GET()
        anime_list = r['stats']['statuses']['anime']
        stats_dict = {
            'planned': anime_list[0]['size'],
            'watching': anime_list[1]['size'],
            'completed': anime_list[2]['size'],
            'on_hold': anime_list[3]['size'],
            'dropped': anime_list[4]['size'],
        }
        return pd.DataFrame(data={
            'type': list(stats_dict.keys()),
            'size': stats_dict.values(),
        })
    @to_df('stars', 'amount')
    def get_df_scores(self, member: str) -> DataFrame:
        r = self.api.users(member).GET()
        stats = r['stats']
        return self.convert_to_dict('scores', stats, append=' stars')

    @to_df('name', 'amount')
    def get_df_types(self, member: str) -> DataFrame:
        r = self.api.users(member).GET()
        stats = r['stats']
        return self.convert_to_dict('types', stats)

    @to_df('rate', 'amount')
    def get_df_ratings(self, member: str) -> DataFrame:
        r = self.api.users(member).GET()
        stats = r['stats']
        return self.convert_to_dict('ratings', stats)

    def get_fig_w_ptw(self, dropdown: list, title: str):
        df = a.get_df_w_ptw(str(dropdown[-1]))
        fig = px.histogram(
            df,
            y="type",
            x='size',
            color='size',
            color_discrete_sequence=[
                '#e5d82a',
                '#abda52',
                '#2de133',
                '#0cb5e4',
                '#ab2626',
            ],
            width=800,
            height=400,
            title=f'{title} for user: {dropdown[-1]}',
        )

        fig.update_traces(showlegend=True, )
        return fig

    def get_fig(self, df: DataFrame, title: str, user:str,  y: str, x: str,):
        fig = px.histogram(
            df,
            y=y,
            x=x,
            color=x,
            width=800,
            height=400,
            title=f'{title} for user: {user}',
        )

        fig.update_traces(showlegend=True, )
        return fig

    def get_title_by_ids(self, ids: list, trottle: float=0.0) -> DataFrame:
        df = pd.DataFrame()
        for num, i in enumerate(ids):
            r = self.api.animes(i).GET()
            time.sleep(trottle)
            stats_dict = {
                'id': r['id'],
                'name_en': r['name'],
                'name_ru': r['russian'],
                'ep_max': r['episodes'],
            }
            df = pd.concat([df, pd.DataFrame(stats_dict, index=[num])]) 
        return df
    def get_id_list(self):
        r = self.api.animes((1, 28977)).GET()
        print(r)


class ShiAuth(object): 
    '''docstring for ClassName'''
    def __init__(self, *arg):
        super(ShiAuth, self).__init__()
        self.CLIENT_ID = os.getenv('CLIENT_ID')
        self.CLIENT_SECRET = os.getenv('CLIENT_SECRET')
        # self.AUTH_CODE = os.getenv('AUTH_CODE')

        self.init_api()

    def init_api(self, ):
        def token_saver(token: dict):
            with open('token.json', 'w') as f:
                f.write(json.dumps(token))

        session = Shikimori('APP_NAME', 
            client_id=self.CLIENT_ID, 
            client_secret=self.CLIENT_SECRET, 
            token_saver=token_saver)

        # code = input('Authorization Code: ')
        
    def request_for_auth_code(self, ):
        print(session.get_auth_url())

    def fetch_token(self, ):
        self.token = self.session.fetch_token(self.AUTH_CODE)
        print(self.token)


if __name__ == '__main__':
    # a = ShiNoAuth()
    from member_list import members
    # d = a.get_df_ratings(members[1])
    # # d = a.get_df_types(members[1])
    # # d = a.get_df_scores(members[1])
    # print(d, type(d))
    # a.get_fig(d, 'ttle', members[-1], 'rate', 'amount', ).show()
    a = ShiNoAuth()
    # ob = a.get_title_by_ids([1, 32998, 40052])

    # print(ob, type(ob))
    a.get_id_list()