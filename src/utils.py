from datetime import datetime

# API labels from Binance
labels_aggTrades = ['Aggregate tradeId', 'Price', 'Quantity', 'First TradeId', 'Last tradeId', 'Timestamp', 'Was the buyer the maker?', 'Was the trade the best price match?']
labels_klines = ["Time", "Open", "High", "Low", "Close", "Volume", "Close Time", "Quote Asset", "Number of Trades", "Taker buy base", "Taker buy Quote", "Ignore"]

# parse dates from Binance CSV (timestamp)
def parse_dates(timestamp: str):
    """
    
    """
    return datetime.utcfromtimestamp(int(timestamp)/1000)

if __name__ == "__main__":
    pass