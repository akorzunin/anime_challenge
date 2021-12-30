
from flask import Flask, app, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
import datetime
import pandas as pd
from pandas.core.frame import DataFrame
from SHIKI_API import ShiNoAuth, ShiAuth
from member_list import members
import yaml

#import blueprints
from legacy import legacy

#load .env variables
import os
from dotenv import load_dotenv
load_dotenv()
G_DRIVE_PATH = os.getenv('G_DRIVE_PATH')
DOCKER = int(os.getenv('DOCKER'))
DEBUG = bool(os.getenv('DEBUG', False))

#define latensy to shikimori API [s]
TROTTLE = 1

app = Flask(__name__)
# handle blueprints
app.register_blueprint(legacy, url_prefix='/legacy')
# get content of legacy sheet
SHEET_FOLDER_PATH = 'xd quest'
folder_content_html = [''.join(i.split(".")[:-1]) for i in os.listdir(SHEET_FOLDER_PATH) if i.split(".")[-1] == 'html']

# Import Dash application
from plotlydash.dashboard import init_dashboard

# render dashboard template
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('dashboard.jinja2')

a = ShiNoAuth()

# dict w/ common data to be rendered in templates
defaults = {
    'members': members,
    'folder_content_html': folder_content_html,
    # 'url_for': url_for,
}
# attach dashboard to flask
app = init_dashboard(
    app,
    # dashboard template content
    html_layout=template.render(
        content='_',
        **defaults,
        )
    )

# attach SQL to flask
db_name = 'database/member_lists.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# this variable, db, will be used for all SQLAlchemy commands
db = SQLAlchemy(app)

class Member(db.Model): 
    __tablename__ = 'members_titles'
    id = db.Column(db.Integer, primary_key=True)
    title_id = db.Column(db.Integer)
    name_en = db.Column(db.String(255))
    name_ru = db.Column(db.String(255))
    max_ep = db.Column(db.Integer)
    from_usr = db.Column(db.String(100))
    to_usr = db.Column(db.String(100))

    def __init__(self, title_id, name_en, name_ru, max_ep, from_usr, to_usr):
        self.title_id = title_id
        self.name_en = name_en
        self.name_ru = name_ru
        self.max_ep = max_ep
        self.from_usr = from_usr
        self.to_usr = to_usr

# rename columns in df
# Use Unicode Character “⠀” (U+2800) to prevent line breaks
rename_dict = {
    'id': '№',
    'to_usr': 'to⠀user',
    'from_usr': 'from⠀user',
    'max_ep': 'ep',
    'name_en':'title name [en]',
    'name_ru':'title name [ru]',
    'title_id': 'title⠀id',
    }

def format_df(df: DataFrame) -> DataFrame:
    '''format DataFrame to render in jinja2'''
    # change db index to number of row
    df['id'] = df.index
    df['to_usr'] = df['to_usr'].apply(lambda x: x[:-2])
    # Use Unicode Character “⠀” (U+2800) to prevent line breaks
    df = df.rename(columns=rename_dict)
    return df

@app.route('/')
def home():
    return render_template('index.jinja2', 
                        content=members, 
                        **defaults,
                        )

@app.route('/rules')
def rules():
    return render_template(
        'rules.jinja2', 
        **defaults,
        content='_')

@app.route('/all_to_others')
def lists_to_others():

    df_dict = {}
    for username in members:
        df = pd.read_sql(f'SELECT * FROM members_titles WHERE "from_usr" LIKE "{username}%"',
            'sqlite:///' + db_name, 
            # index_col='id',
            )
        df_dict[username] = format_df(df)


    return render_template(
        'lists.jinja2', 
        column_names=df_dict[members[-1]].columns.values, 
        row_data={i: list(df_dict[i].values.tolist()) for i in members},      
        link_column="title⠀id", 
        zip=zip,
        **defaults,
        preposition='from',       
        )

@app.route('/all_from_others')
def lists_from_others():

    df_dict = {}
    for username in members:
        df = pd.read_sql(f'SELECT * FROM members_titles WHERE "to_usr" LIKE "{username}%"',
            'sqlite:///' + db_name, 
            # index_col='id',
            )
        df_dict[username] = format_df(df)

    return render_template(
        'lists.jinja2', 
        column_names=df_dict[members[-1]].columns.values, 
        row_data={i: list(df_dict[i].values.tolist()) for i in members},      
        link_column="title⠀id", 
        zip=zip,
        **defaults,  
        preposition='to',       
        )

@app.route('/library')
def library():
    return render_template(
        'library.jinja2',
        **defaults,
        content='_')

@app.route('/<username>/to_others')
def user_list(username=None):
    # read data from database
    df = pd.read_sql(f'SELECT * FROM members_titles WHERE "from_usr" = "{username}"',
            'sqlite:///' + db_name, 
            # index_col='id',
            )
    
    df = format_df(df)
    return render_template(
        'user_list.jinja2',
        **defaults, 
        column_names=df.columns.values, 
        row_data=list(df.values.tolist()),
        link_column="title⠀id", 
        zip=zip,
        content=username)

@app.route('/<username>/from_others')
def user_list_(username=None):
    # read data from database
    df = pd.read_sql(f'SELECT * FROM members_titles WHERE "to_usr" LIKE "{username}%"',
            'sqlite:///' + db_name, 
            # index_col='id',
            )
    df = format_df(df)
    return render_template(
        'user_list.jinja2',
        **defaults, 
        column_names=df.columns.values, 
        row_data=list(df.values.tolist()),
        link_column="title⠀id", 
        zip=zip,
        content=username)

@app.route('/myendpoint', methods=['POST', 'GET'])
def myendpoint():
    return render_template('index.jinja2')



@app.route('/admin')
def admin():
    # diif response for admin endpoint
    # on hoome page
    return redirect(url_for('home'))

if __name__ == '__main__':
    if DEBUG:
        app.run(debug=DEBUG, host='0.0.0.0', port=5050)
    else:
        from waitress import serve
        serve(app, host="0.0.0.0", port=5050)
