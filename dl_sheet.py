
import requests
import zipfile
from typing import Union

def dl_sheet(**kwargs) -> Union[int, str]:
    '''kwargs: download_file_name, destination_folder, url'''
    download_file_name = kwargs.pop('dl_file_name', 'xd_quest.zip')
    destination_folder = kwargs.pop('folder', 'xd quest')
    url = kwargs.pop('url', 'https://docs.google.com/spreadsheets/d/11-CDLcn-MQ0WXbHtWxa5Zc8lrLIfkgbuSSqVXVo9IyI/export?format=zip')
    r = requests.get(url)
    # download content
    with open(download_file_name, 'wb+' ) as f:
        f.write(r.content)
    # unzip file
    with zipfile.ZipFile(download_file_name, 'r') as zip_ref:
        zip_ref.extractall(destination_folder)
    return r.status_code, destination_folder

if __name__ == '__main__':
    print(dl_sheet())

