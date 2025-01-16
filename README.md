# Live_Trading_Bot
This is my Live Trading Bot

### Step 1:  
- Create the Python environment (to activate it "venv\Scripts\activate").  
- Create an OANDA demo account and connect to the API.  

### Step 2:  
- Create a folder named **exploration** to conduct tests on the API directly within Jupyter Notebook, aiming to display the elements obtained through API requests (prices, granularities, trades).  
- Create a folder named **data** to store candlestick data collected via the API.  

### Step 3 (Building on what was done in Jupyter Notebook):  
- Create a `main.py` file to execute requests and visualize the results.  
- Create a folder named **constants** to store all authentication details (these will be hidden during GitHub commits).  
- Create a folder named **api** to manage API requests to OANDA.  

### Step 4 (Codes here will be run via `main.py`):  
- Create a file named **models**, which will contain the codes tested in the **exploration** folder. Create a file `instruments.py` that defines currency pair (instrument) information.  
- Create a folder named **simulation** to store code for technical analysis performed on candlesticks in Jupyter Notebook:  
  - `ma_cross.py`: Simulates trades using the moving average method.  
  - `ma_excel.py`: Exports the results of trades from `ma_cross.py` to an Excel file.  

### Step 5:  
- Create a `db.py` file in a **db** folder to manage connections to MongoDB for data storage.  
- Create a folder named **infrastructure**, including the `instrument_collection.py` script to retrieve information on multiple currencies simultaneously.  
- Create a script named `collect_data.py` to define currency pairs, granularities, and the period for data collection. This script uses `instrument_collection` over a broader range and stores results in `.pkl` files.  

### Step 6:  
- Create a folder named **technicals** to store scripts for additional technical indicators (e.g., Bollinger Bands, ATR, Keltner Channels, RSI, MACD, or candlestick patterns).  
- Use MACD (Moving Average Convergence Divergence) and EMA (Exponential Moving Average) alongside a script named `guru_tester.py` for instant trading. This script will be stored as `ema_macd_start.py` in the **simulation** folder.  
- To execute the above script across multiple pairs simultaneously, create `ema_macd_mp.py` (mp = multiprocessing) in the **simulation** folder.  

### Step 7:  
- Define trades in the script `Oanda_api.py` and create `api_tests.py` at the root directory for trade execution testing.  

### Step 8 (Bot Execution):  
- The bot retrieves candlestick data, identifies signals using technical indicators (e.g., Bollinger Bands), checks trends, evaluates risks, and places trades (refer to the workflow diagram).  
- Create `bot.py` in a **bot** folder to execute trades. Use `settings.json` to define trade validation parameters for the bot.  
- Create the following scripts for bot functionality:  
  - **technicals_manager.py**  
  - **trade_manager/trade_risk_calculator.py** (verifies if the risk is acceptable for trade placement)  
  - **candle_manager.py**  
- In the **infrastructure** folder, create `logwrapper.py` to display logs during bot execution.  
- Create `run_bot.py` at the root level to launch the bot.  

### Step 9:  
- Investigate how to fetch live data for immediate use (avoiding constant storage of data before using it).  
- Use multithreading to process data sequentially over time.  
- Develop a bot (`stream_bot`) to execute trades with live prices.  

### Step 10:  
- Create a folder named **scraping** to house scripts for data scraping, enabling visualization through a locally created React app.  
- Deploy the bot.  

**Note:**  
- **Buy** = Betting on a price increase.  
- **Sell** = Betting on a price decrease.  
