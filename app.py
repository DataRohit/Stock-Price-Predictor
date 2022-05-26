import streamlit as st
from helpers import *

# Initializing the StockOperations class from helpers.py
stock_operations = StockOperations()

# Sidebar
st.sidebar.title("Selections/Filters")

# -----Sidebar Section 1 - Start-----

st.sidebar.header("Company Selector")

# Company Selection
company = st.sidebar.selectbox(
    'Company Name', (stock_operations.all_company_names()))

# Stock Exchange Selection
exchange = st.sidebar.selectbox('Stock Exchange', ("BSE", "NSE"))

# Get Company ID
company_id = stock_operations.get_company_id(company, exchange)

# Display the Company ID to the user
st.sidebar.text_input('Company ID : ', company_id, disabled=True)

# -----Sidebar Section 1 - End-----

# -----Sidebar Section 2 - Start-----

# Sidebar - Section 2
st.sidebar.header("Period/Interval Selector")

# Get the compatible period - interval dictionary
period_interval_dict = stock_operations.get_period_interval_dict()

# Period and Interval Selection
period = st.sidebar.selectbox('Period', period_interval_dict.keys())
interval = st.sidebar.selectbox('Interval', period_interval_dict[period])

# -----Sidebar Section 2 - End-----

# Main View Port

st.title('Stock Price Predictor')

# Display the selected company, stock exchange and company id
st.markdown(
    f"<h5>Company Selected: {company} - {exchange}</h5>", unsafe_allow_html=True)
st.markdown(
    f"<h5>Company Ticker (ID): {company_id}</h5>", unsafe_allow_html=True)

# Get Stock Info
stock_info = stock_operations.get_stock_info(company_id)

# -----Main Section 1 - Start-----

st.header("Price Summary")

format_money = FormatMoney()

# Display the basic stock price data
col1, col2, col3, col4 = st.columns(4)

col1.markdown(custom_streamlit_metric("Today's High", format_money.format_amount(
    stock_info['dayHigh'])), unsafe_allow_html=True)
col2.markdown(custom_streamlit_metric("Today's Low", format_money.format_amount(
    stock_info['dayLow'])), unsafe_allow_html=True)
col3.markdown(custom_streamlit_metric("52 Week High", format_money.format_amount(
    stock_info['fiftyTwoWeekHigh'])), unsafe_allow_html=True)
col4.markdown(custom_streamlit_metric("52 Week Low", format_money.format_amount(
    stock_info['fiftyTwoWeekLow'])), unsafe_allow_html=True)

# -----Main Section 1 - End-----

# -----Main Section 2 - Start-----

# Display Selected Period and Interval
st.header("Plots/Graphs")
st.markdown(f"<h6>Selected Period: {period}</h6>", unsafe_allow_html=True)
st.markdown(f"<h6>Selected Interval: {interval}</h6>", unsafe_allow_html=True)

custom_plotly_plots = CustomPlotlyPlots(company_id, period, interval)

fig = custom_plotly_plots.candle_plot()
print(type(fig))
st.plotly_chart(fig)

fig = custom_plotly_plots.line_plot()
st.plotly_chart(fig)

# -----Main Section 2 - Start-----

# -----Main Section 3 - Start-----

st.header("Future Prediction Plot")

try:
    fig = custom_plotly_plots.prediction_plot()
    st.plotly_chart(fig)
except:
    st.subheader("Future Predicion Currenty Unavailable for this stock!")

# -----Main Section 3 - Start-----
