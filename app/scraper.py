import re
import requests
from typing import Any, List
from bs4 import BeautifulSoup
from csv_writer import CSVWriter
from collections import namedtuple
from abc import ABC, abstractmethod


NewsWebsite = namedtuple('NewsWebsite', ['url', 'headline'])
news_websites = [
    NewsWebsite('https://www.bbc.com/', 'h2'),
    NewsWebsite('https://edition.cnn.com/', 'span'),
    NewsWebsite('https://www.indiatoday.in/', 'a'),
]

class DomainExtractor(ABC):
    domain_ptn = r'https?://([^/]+)/' # Regular expression for domain extraction

    @abstractmethod
    def get_domain(self, address: str) ->  str:
        pass

class DefaultDomainExtractor(DomainExtractor):
    def get_domain(self, address: str) -> str:
        if not address:
            return address
        match = re.search(self.domain_ptn, address)
        if match:
            subdomain = match.group(1)
            name = subdomain.split('.')[1]
            return name
        
class WebScraper(ABC):
    encoding = 'ISO-8859-1'

    @abstractmethod
    def get_page(self, url: str) -> bytes | None:
        pass

class RequestsWebScrapper(WebScraper):
    def get_page(self, url: str) -> bytes | None:
        response = requests.get(url)
        if response.status_code != 200:
            print(f'{url} status {response.status_code}')
            return
        response.encoding = self.encoding
        return response.content
    
class HeadlineExtractor(ABC):
    false_words = set(['\n', '\n\n', ' ', ''])

    def get_headlines(self, domain: str, provider: str, html_content: bytes | str, headline_tag: str) -> List[dict[str, str]]:
        pass

class BS4HeadlineExtractor(HeadlineExtractor):
    def get_headlines(self, domain: str, provider: str, html_content: Any, headline_tag: str) -> List[str] | None:
        headlines = [] # To store the headline links, title, link
        if html_content is None:
            return None
        soup = BeautifulSoup(html_content, 'html.parser')
        for a in soup.find_all('a'):
            if 'href' in a.attrs:
                title_tag = a.find(headline_tag)
                headline_link = a.get('href')
                headline_link = headline_link if headline_link.startswith('https://') else f'{domain}{headline_link[1:]}'
                if title_tag and title_tag.text not in self.false_words:
                    headline_text = title_tag.text
                elif a.get('title') and len(a.get('title')) > 30:
                    headline_text = a.get('title')
                else:
                    continue
                if headline_link not in list(map(lambda x: x['link'], headlines)):
                    headlines.append({
                        'provider': provider,
                        'title': headline_text, 
                        'link': headline_link
                    })
        return headlines


if __name__ == '__main__':

    domain_extractor = DefaultDomainExtractor()
    web_scraper = RequestsWebScrapper()
    headline_extractor = BS4HeadlineExtractor()

    for news in news_websites:

        url = news.url
        title_tag = news.headline

        provider = domain_extractor.get_domain(url)
        html_content = web_scraper.get_page(url)

        if html_content:
            headlines = headline_extractor.get_headlines(url, provider, html_content, title_tag)
        else:
            print(f'No content found for {provider}')
            headlines = None

        if headlines:
            fields = headlines[0].keys()
            CSVWriter.write(filepath=f'./{provider}_news.csv', data=headlines, headers=fields)
        
