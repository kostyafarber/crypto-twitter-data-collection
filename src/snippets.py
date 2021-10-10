# snippets

# convert binance api convert timestamp to date
datetime.datetime.fromtimestamp(___/1000)

# set default size in matplotlib
matplotlib.rcParams['figure.figsize'] = (20, 10)

# snippet that generates date ranges (not needed after discovery of glob YAY)
data_path = '../data/data/spot/monthly/aggTrades/ETHBTC/*'

# Create date ranges in format yyyy-mm for 2017 until now
DATES_YEARS = ["2017", "2018", "2019", "2020", "2021"]
DATES_MONTHS = [str(month).zfill(2) for month in range(1,13)]

DATE_RANGE = []

for year in DATES_YEARS:

    for month in DATES_MONTHS:

       year_month = "-".join([year, month])

       DATE_RANGE.append(year_month)

# grab all the file neames 
data_path = '../data/data/spot/monthly/aggTrades/ETHBTC/*'

files = glob.glob(data_path)