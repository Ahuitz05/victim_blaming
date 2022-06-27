import pandas as pd
import json
import newspaper
from newspaper import Config
from newspaper import Article
from newspaper.utils import BeautifulSoup
from sqlalchemy import create_engine

newspapers = pd.read_csv('newspaper_data.csv')

name_websiste = newspapers[['info_Nombre de la publicación aprobada por el Indautor', 'info_Página electrónica']]

name_websiste = name_websiste.drop_duplicates('info_Página electrónica')
name_websiste.dropna(inplace=True)

name_websiste['info_Página electrónica'] = 'http://' + name_websiste['info_Página electrónica'].str.strip(' ')



config = Config()
test_paper = newspaper.build(name_websiste['info_Página electrónica'][0], config=config, memoize_articles=False, language='es')

url = []
title = []
authors = []
text = []
date = []

for article in test_paper.articles:
    article.download()
    article.parse() 

    url.append(article.url)
    title.append(article.title)
    authors.append(article.authors)
    text.append(article.text)

    soup = BeautifulSoup(article.html, 'html.parser')

    for i in soup.findAll('time'):
            if i.has_attr('datetime'):
                date.append(i['datetime'])

df = pd.DataFrame(list(zip(url, title, authors, text, date)),
            columns =['url', 'title', 'authors', 'text', 'date'])

import time

today = time.strftime("%Y-%m-%d")

df.date = pd.to_datetime(df.date)

df = df.loc[(df.date >= today)]

engine = create_engine('postgresql://root:root@localhost:5432/daily_news_articles')

df.to_sql(name='daily_news_articles', con=engine, if_exists='append')

