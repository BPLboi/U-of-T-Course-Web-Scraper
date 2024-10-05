import requests
from bs4 import BeautifulSoup


def scrape_ttb():
    "Extracts the html from a given website"

    # app_root = open("app-root.html", "r")
    # response = app_root.read()
    # soup = BeautifulSoup(response.text, 'html.parser')

    url = 'https://artsci.calendar.utoronto.ca/course/csc241h1'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    with open('./Data/csc241.html', 'w') as f:
        f.write(soup.prettify())

    all_divs = soup.find_all('div')
    for div in all_divs:
        if div.get('aria-label') is not None:
            text = div.text
            if text.__contains__(' - '):
                (course, title) = text.split(' - ')
                print(course)

if __name__ == '__main__':
    scrape_ttb()