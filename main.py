import pandas as pd
from pathlib import Path
from quantbt.data import get_trading_strategy_data

# |%%--%%| <IiXzmyDfSR|WvFRZKpLuB>


# In order to find this information you need to go under the "API and historical data" tab
# Example: https://tradingstrategy.ai/trading-view/ethereum/uniswap-v3/eth-usdc-fee-5/api-and-historical-data
pair_id = 2697765
exchange_type = "uniswap_v3"
name = "uniswap_v3-ethereum-WETH-USDC-1h"
tf = "1h"

# |%%--%%| <WvFRZKpLuB|jC9QbYtoDy>

# df = get_trading_strategy_data(pair_id, exchange_type, tf, "2011-11-04")
df = get_trading_strategy_data(pair_id, exchange_type, tf, "2022-11-04")
print(df)

data_directory_path = Path("./data")
if not data_directory_path.exists():
    data_directory_path.mkdir(parents=True, exist_ok=True)

df.to_parquet(f"./data/{pair_id}-{exchange_type}-{tf}.parquet")

# |%%--%%| <jC9QbYtoDy|2nBa3UKPa1>


import quantbt.indicators as ind
from quantbt.strategies.S_base import S_base
from quantbt.core.enums import CommissionType, DataType, TradeSizeType
import pandas_ta as ta


data = pd.read_parquet(f"./data/{pair_id}-{exchange_type}-{tf}.parquet")
data = data[0:300]


class SMA_Cross_Strategy(S_base):
    def generate_signals(self):
        short_period, long_period = params

        data["sma_short"] = ta.sma(close=data.close, length=short_period)
        data["sma_long"] = ta.sma(close=data.close, length=long_period)
        self.sma_short = data["sma_short"]
        self.sma_long = data["sma_long"]

        self.long = ind.cross_above(self.sma_short, self.sma_long)
        self.short = ind.cross_below(self.sma_short, self.sma_long)

        return {
            "long_entries": self.long,
            "long_exits": self.short,
            "short_entries": self.short,
            "short_exits": self.long,
        }


strategy_settings = {
    "initial_capital": 100_000,
    "commission": 0.0005,
    "commission_type": CommissionType.PERCENTAGE,
    "default_trade_size": 0.2,
    "trade_size_type": TradeSizeType.PERCENTAGE,
}

st = SMA_Cross_Strategy(data, **strategy_settings)

# |%%--%%| <2nBa3UKPa1|zXtpVf1yt0>

# We will be doing a 5-SMA and 23-SMA crossover
params = (5, 23)
st.from_signals(params)

# |%%--%%| <zXtpVf1yt0|5Tj0AYmXlC>

st.plot_equity()

# |%%--%%| <5Tj0AYmXlC|hxdiilfO8n>

st.get_trades()

# |%%--%%| <hxdiilfO8n|uohTq34rMk>

import matplotlib
import quantbt as qbt


plotting = qbt.lib.plotting
subplots = [
    plotting.add_line_plot(st.sma_short),
    plotting.add_line_plot(st.sma_long),
    plotting.add_markers(
        st.long, data.close, color="green", marker_type=matplotlib.markers.CARETUP
    ),
    plotting.add_markers(
        st.short, data.close, color="red", marker_type=matplotlib.markers.CARETUP
    ),
]

qbt.lib.plotting.mpf_plot(data, subplots=subplots)
