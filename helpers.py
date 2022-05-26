import pandas as pd  # pandas for dataset/dataframe operations
import yfinance as yf  # yfinance for getting live stock price data
import plotly.graph_objects as go  # plotly for interactive plots
from statsmodels.tsa.ar_model import AutoReg  # AutoReg ML Model for predictions


class StockOperations():
    def __init__(self):
        # Loading the list of 4000+ BSE Listed Stocks
        bse_stock_list = pd.read_csv("./bse_stock_data.csv")

        self.bse_stock_list = bse_stock_list

    def all_company_names(self):
        # Returns the list of all company names
        return self.bse_stock_list["Name"].unique()

    def get_company_id(self, name, exchange):
        # Get the ID for the user selected company
        company_id = self.bse_stock_list["ID"].loc[self.bse_stock_list["Name"]
                                                   == name].values[0]

        if exchange == "BSE":
            return company_id + ".BO"
        else:
            return company_id + ".NS"

    def get_stock_info(self, id):
        # Get stock info for the selected company
        return yf.Ticker(id).info

    def get_period_interval_dict(self):
        # Compatible intervals for the total period
        return {
            "5d": ("5m", "15m", "30m", "1h"),
            "1mo": ("1h", "1d", "1wk"),
            "3mo": ("1h", "1d", "1wk"),
            "6mo": ("1h", "1d", "1wk"),
            "1y": ("1h", "1d", "1wk", "1mo"),
            "2y": ("1d", "1wk", "1mo", "3mo"),
            "5y": ("1d", "1wk", "1mo", "3mo"),
        }


class FormatMoney():
    def __init__(self):
        pass

    def format_amount(self, amount):
        # Add's the commas and the symbol to the amount
        s, *d = str(amount).partition(".")
        r = ",".join([s[x-2:x]
                      for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
        return "₹" + "".join([r] + d)

    def format_cash(self, amount):
        # Formats the amount to be displayed in the cash
        def truncate_float(number, places):
            return self.format_amount(int(number * (10 ** places)) / 10 ** places)

        # Truncate large amount of cash for better display
        if amount < 1e5:
            return self.format_amount(amount)

        if 1e5 <= amount < 1e7:
            return str(truncate_float(number=amount / 1e7 * 100, places=2)) + " L"

        if amount > 1e7:
            return str(truncate_float(number=amount / 1e7, places=2)) + " Cr"


def custom_streamlit_metric(label, data):
    # Custom streamlit metic to display the data
    return f"<p style='margin:0px;'><label>{label}</label></p><h5 style='padding:0px; font-size:1.3rem'>{data}</h5>"


class CustomPlotlyPlots():
    def __init__(self, ticker, period, interval):
        # Get the stock data for training and testing the model
        self.ticker = ticker
        
        try:
            self.stock_data = yf.download(
                tickers=self.ticker,
                period=period,
                interval=interval,
                group_by='ticker',
                auto_adjust=True,
                prepost=True,
                threads=True
            )
        except:
            df = yf.download(
                tickers=self.ticker,
                period="1mo",
                interval="1d",
                group_by="ticker",
                auto_adjust=True,
                prepost=True,
                threads=True
            )

    def line_plot(self):
        # Simple Line plot for the stock price
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=self.stock_data.index,
                y=self.stock_data.Close,
                mode="lines",
                line_shape='spline',
                line=dict(color="#92B4EC", width=3),
                name="Close"
            )
        )

        fig.update_layout(
            title=dict(
                text="Historical Stock Closing Price - Line Plot",
                font=dict(
                    size=22,
                    family="Source Sans Pro"
                )
            ),
            xaxis_title="Date",
            yaxis_title="Stock Price (₹)",
            height=500,
            width=800,
            hovermode='x unified',
            template="plotly"
        )

        fig.layout.yaxis.fixedrange = True

        return fig

    def candle_plot(self):
        # Candle plot for the stock price
        fig = go.Figure(
            go.Candlestick(
                x=self.stock_data.index,
                open=self.stock_data['Open'],
                high=self.stock_data['High'],
                low=self.stock_data['Low'],
                close=self.stock_data['Close'],
            )
        )

        fig.update_layout(
            title=dict(
                text="Historical Stock Price - Candle Stick Plot",
                font=dict(
                    size=22,
                    family="Source Sans Pro"
                )
            ),
            xaxis_title="Date",
            yaxis_title="Stock Price (₹)",
            height=500,
            width=800,
            hovermode='x unified',
            template="plotly"
        )

        fig.layout.yaxis.fixedrange = True

        return fig

    def prediction_plot(self):
        # Function to train and test the model
        # Using the trained model to predict the stock price

        # Download the required data for training and testing
        try:
            df = yf.download(
                tickers=self.ticker,
                period="1y",
                interval="1d",
                group_by="ticker",
                auto_adjust=True,
                prepost=True,
                threads=True
            )
        except:
            df = yf.download(
                tickers=self.ticker,
                period="max",
                interval="1d",
                group_by="ticker",
                auto_adjust=True,
                prepost=True,
                threads=True
            )

        # Setting the date-time index frequency to day
        df = df.asfreq("D")
        # Fill the missing values with the previous value
        df = df.fillna(method="ffill")

        # Seperating the training and testing data
        train_df = df.iloc[:round(len(df) * 0.8)]
        test_df = df.iloc[round(len(df) * 0.8):]

        # Initializing the AutoReg Model with full data
        model = AutoReg(df["Close"], 100, seasonal=True)
        # Fitting the model
        res = model.fit()

        # Set the starting point and end point for the prediction
        start = len(train_df) + len(test_df) - 1
        end = start + 50

        # Get the prediction for the next 50 days
        prediction = res.predict(start, end).rename("Prediction")

        # Plot the test data followed by the prediction
        fig = go.Figure()

        # First line for plotting the test data
        fig.add_trace(
            go.Scatter(
                x=test_df.index,
                y=test_df["Close"],
                mode="lines",
                line_shape='spline',
                line=dict(color="#646FD4", width=3),
                name="Historical Data"
            )
        )

        # Second line for plotting the predictions
        fig.add_trace(
            go.Scatter(
                x=prediction.index,
                y=prediction.values,
                mode="lines",
                line_shape='spline',
                line=dict(color="#FF5D5D", width=3),
                name="Future Prediction"
            )
        )

        fig.update_layout(
            title=dict(
                text="Company Stock Price Future Prediction",
                font=dict(
                    size=22,
                    family="Source Sans Pro"
                )
            ),
            xaxis_title="Date",
            yaxis_title="Stock Price (₹)",
            height=500,
            width=800,
            hovermode='x unified',
            template="plotly"
        )

        fig.layout.yaxis.fixedrange = True

        return fig
