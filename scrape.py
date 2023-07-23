from bs4 import BeautifulSoup
import random
import pandas as pd
import requests


def get_proxy():
    with open('valid_proxies.txt', 'r') as f:
        proxies = f.readlines()
    proxy = random.choice(proxies).strip()
    return proxy

def get_page(url):
    proxy = get_proxy()
    print('Proxy:', proxy)
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, proxies={"http": proxy, "https": proxy}, timeout=3, headers=headers)
        print(response.status_code)
        return response
    except:
        return get_page(url)


def scrape():
    Marka, Model, Year, Price = [], [], [], []
    urls = ['https://kolesa.kz/cars/almaty/?page=' + str(i) for i in range(2, 502)]
    for url in urls:
        try:
            response = get_page(url)
            print('text', response.text[:5])
            soup = BeautifulSoup(response.text, 'html.parser')
            print('Extracting page number:', url.replace('https://kolesa.kz/cars/almaty/?page=', ''))
            Marka.extend([i.text.split('\n')[0].strip().split(' ', 1)[0] for i in soup.find_all(class_='a-card__info')])
            Model.extend([i.text.split('\n')[0].strip().split(' ', 1)[1:] for i in soup.find_all(class_='a-card__info')])
            Year.extend([i.text.strip()[:4] for i in soup.find_all(class_='a-card__description')])
            Price.extend([i.text.strip().replace('\xa0', '')[:-1] for i in soup.find_all(class_='a-card__price')])
        except:
            print('Failed!')

    df = pd.DataFrame({'Marka': Marka, 'Model': Model, 'Year': Year, 'Price': Price})
    return df

df = scrape()
df.to_csv('cars.csv')

print(df)