
from flask import Flask, app, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
import datetime
import pandas as pd
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

@app.route('/lists')
def lists():
    df_usr_dict = {}
    # for loop for all members
    for username in members:
        # read yaml file of member to list of ids
        # read from G_DRIVE
        # sleep(0.4)
        if DOCKER:
            filename = f'{G_DRIVE_PATH}/{username}_list.yaml'
        else: 
            filename = f"G:\\My Drive\\ANIME_CHALLENGE\\{username}_list.yaml"
        with open(filename, 'r') as f:
            dl = yaml.load(f, Loader=yaml.FullLoader)
            # left only valid ids
            ids = [i for i in dl.values() if isinstance(i, int)]
        # get df w/ titles
        dfr = a.get_title_by_ids(ids, TROTTLE)
        # name of user who assigned title
        dfr['from user'] = username
        # user who need to watch title
        dfr['to user'] = [key for key, val in dl.items() if isinstance(val, int)] 
        # df w/ all titles of member list
        df_usr_dict[username] = dfr

    return render_template(
        'lists.jinja2', 
        column_names=dfr.columns.values, 
        row_data={i: list(df_usr_dict[i].values.tolist()) for i in members},      
        link_column="id", 
        zip=zip,
        **defaults,        
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
    # change db index to number of row
    df['id'] = df.index
    df = df.rename(columns={'id': '№'})
    return render_template(
        'user_list.jinja2',
        **defaults, 
        column_names=df.columns.values, 
        row_data=list(df.values.tolist()),
        link_column="title_id", 
        zip=zip,
        content=username)

@app.route('/<username>/from_others')
def user_list_(username=None):
    # read data from database
    df = pd.read_sql(f'SELECT * FROM members_titles WHERE "to_usr" LIKE "{username}%"',
            'sqlite:///' + db_name, 
            # index_col='id',
            )
    # change db index to number of row
    df['id'] = df.index
    df = df.rename(columns={'id': '№'})
    return render_template(
        'user_list.jinja2',
        **defaults, 
        column_names=df.columns.values, 
        row_data=list(df.values.tolist()),
        link_column="title_id", 
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
    app.run(debug=True, host='0.0.0.0', port=5050)
