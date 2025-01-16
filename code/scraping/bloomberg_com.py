import cloudscraper
from bs4 import BeautifulSoup

def get_article(card):
    return dict(
        headline=card.get_text(),
        link='https://www.reuters.com' + card.get('href')
    )

def bloomberg_com():

    # Create a cloudscraper instance
    scraper = cloudscraper.create_scraper()

    # Fetch the webpage content (You can change the link to change the pair)
    url = "https://www.reuters.com/business/finance/"
    response = scraper.get(url)
    html = response.text

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    links = []
    cards = soup.select('[class^="media-story-card__body"]')
    # Append the first link of the website
    if len(cards) :
        links.append(get_article(cards[0].find('a', {'data-testid':'Link'})))

    #Append other links
    for card in cards:       
        ca = card.find('a', {'data-testid':'Heading'})
        if ca:
            links.append(get_article(ca))          
    return links