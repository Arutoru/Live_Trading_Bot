import cloudscraper
import pandas as pd
from bs4 import BeautifulSoup
import datetime as dt

import constants.defs as defs

def actionforex_com(pair_name, tf):
    # Create a cloudscraper instance
    scraper = cloudscraper.create_scraper()

    # Fetch the webpage content (You can change the link to change the pair)
    url = f"https://www.actionforex.com/markets/pivot-points/"
    response = scraper.get(url)
    html = response.text

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

   
    pair_name = pair_name.replace('_', '')

    if tf not in defs.TFS:
        tf = 'pivot-h'
    else:
        tf = defs.TFS[tf]

    # pairs = {}
    # id = 0 


    # Extract Data
    pivot_points_table = soup.find(id=tf)
    if pivot_points_table:
        pivot_points_header = [th.get_text(strip=True) for th in pivot_points_table.find_all('th')[1:]]
        pivot_points_rows = pivot_points_table.find_all('tr')[1:] # Skip header of the table
        for row in pivot_points_rows:
            cells = [cell.get_text(strip=True) for cell in row.find_all('td')]
            if not cells:
                break

            # pairs[cells[0]] = {"pair":cells[0], "pair_id":id}
            # id+=1

            if cells[0]==pair_name:
                data = cells[1:]
        
    pivot_points = dict(zip(pivot_points_header, data))
    pivot_points['pair'] = pair_name

    # print(pairs)

    return pivot_points
    
