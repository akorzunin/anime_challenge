from flask import Blueprint, render_template, url_for
from member_list import members
from dl_sheet import dl_sheet
import os
# download google sheet
code, path = dl_sheet()
#get content of folder
if code == 200:
    folder_content = os.listdir(path)
else: print('Failed to load sheet content')
# get names of all html files in folder w/ sheet 
folder_content_html = [''.join(i.split(".")[:-1]) for i in folder_content if i.split(".")[-1] == 'html']

legacy = Blueprint(
    'legacy', 
    __name__, 
    # static_folder='xd quest', 
    # static_url_path='',
    template_folder='xd quest')

# read styles from file
with open('./xd quest/resources/sheet.css', 'r') as f:
    styles = f.read()

@legacy.route('/<list_name>')
def list_name(list_name):
    if list_name in folder_content_html:
        with open(f'./xd quest/{list_name}.html', 'r', encoding='utf-8') as f:
            html_file = f.read()
    else: 
        # handle 404 error
        pass
    return render_template(
        'ebalo_l.jinja2', 
        content=html_file,
        members=members,
        folder_content_html=folder_content_html,
        url_for=url_for,
        # special treatment for some pages in sheet
        styles_txt=styles if list_name in ['eбalo', 'helпер'] else '',
        )