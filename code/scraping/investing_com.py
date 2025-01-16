import cloudscraper
import pandas as pd
from bs4 import BeautifulSoup
import datetime as dt

import constants.defs as defs

def pairurl(pair_name):
    pair_url = pair_name.replace('_', '-')
    return(pair_url.lower())


def investing_com(pair_name):

    # Create a cloudscraper instance
    scraper = cloudscraper.create_scraper()
    
    # Pair name for the url
    pair_url = pairurl(pair_name)
    if pair_url=="eur-usd":
        pair_url=''
    else:
        pair_url+='-'

    print(pair_url)

    # Fetch the webpage content (You can change the link to change the pair)
    url = f"https://www.investing.com/technical/{pair_url}technical-analysis"
    response = scraper.get(url)
    html = response.text

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Initialize lists to store data
    pair_data = []
    moving_averages_data = []
    pivot_points_data = []
    tech_indicators_data = []

    # Verify timeframe
    # card = soup.find('ul', class_='')
    # timeframe = card.select_one('a').get_text().strip()
    # timeframe = int(card.get('data-period'))
    # if tf != timeframe:
    #     return ("Please change the timeframe")


    # Extract pair_name
    card = soup.find(id='techStudiesInnerBoxLeft')
    analysis = soup.select('.summaryTableLine')
    pair_data.append(dict(
        pair=card.select_one('a').get_text().replace("/", "_").strip(),
        value=card.select_one('#lastValue1').get_text().strip(),
        # time=card.select_one('#updateTime').get_text().strip(),
        ma_buy=analysis[0].select_one('#maBuy').get_text().strip(),
        ma_sell=analysis[0].select_one('#maSell').get_text().strip(),
        ti_buy=analysis[1].select_one('#maBuy').get_text().strip(),
        ti_sell=analysis[1].select_one('#maSell').get_text().strip(),

    ))

    # Extract data from the pivot points table
    pivot_points_table = soup.find('table', class_='genTbl closedTbl crossRatesTbl')
    if pivot_points_table:
        pivot_points_header = [th.get_text(strip=True) for th in pivot_points_table.find_all('th')]
        pivot_points_rows = pivot_points_table.find_all('tr')[1:] # Skip header row
        for row in pivot_points_rows:
            cells = [cell.get_text(strip=True) for cell in row.find_all('td')]
            if cells:
                pivot_points_data.append(cells)
        del pivot_points_data[-1]

    # Extract data from the technical indicators table
    tech_indicators_table = soup.find('table', class_='technicalIndicatorsTbl')
    if tech_indicators_table:
        tech_indicators_header = [th.get_text(strip=True) for th in tech_indicators_table.find_all('th')]
        tech_indicators_rows = tech_indicators_table.find_all('tr')[1:] # Skip header row
        for row in tech_indicators_rows:
            cells = [cell.get_text(strip=True) for cell in row.find_all('td')]
            if cells:
                tech_indicators_data.append(cells)
        del tech_indicators_data[-1]  

    # Extract data from the moving average table
    moving_average_table = soup.find('table', class_='movingAvgsTbl')
    if moving_average_table:
        moving_average_header = [th.get_text(strip=True) for th in moving_average_table.find_all('th')]
        moving_average_rows = moving_average_table.find_all('tr')[1:] # Skip header row
        for row in moving_average_rows:
            cells = [cell.get_text(strip=True) for cell in row.find_all('td')]
            if cells:
                moving_averages_data.append(cells)
        del moving_averages_data[-1]  

    
    # Create DataFrames
    df_pair_name = pd.DataFrame.from_dict(pair_data)
    df_pivot_points = pd.DataFrame(pivot_points_data, columns=pivot_points_header)
    df_tech_indicators = pd.DataFrame(tech_indicators_data, columns=tech_indicators_header)
    df_moving_averages = pd.DataFrame(moving_averages_data, columns=moving_average_header)
    
    # Print the DataFrames
    # print("pair Data:")
    # print(df_pair_name)

    # print("\nPivot Points Data:")
    # print(df_pivot_points)

    # print("\nTechnical Indicators Data:")
    # print(df_tech_indicators)

    # print("\nMoving Averages Data:")
    # print(df_moving_averages)

    # For values as the lessons
    df_final_data = pd.concat([df_pair_name, 
                               df_moving_averages.iloc[:1], 
                               df_tech_indicators.iloc[:1]], axis=1)
    # Conversion d'une ligne d'un dataframe en dictionnaire
    dict1 = df_final_data.iloc[0].to_dict()
    dict2 = df_tech_indicators.rename(columns=lambda x: x+'*').iloc[-1].to_dict()
    return {**dict1, **dict2}