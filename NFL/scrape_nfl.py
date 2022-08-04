import pandas as pd
from bs4 import BeautifulSoup
import requests



URL = 'http://www.espn.com/nfl/weekly/leaders/_/week/1/seasontype/2/type/passing'
page = requests.get(URL)

if page.ok:
    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find_all('table')
    df = pd.read_html(str(table))[0]