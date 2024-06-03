import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf
from datetime import datetime
from sklearn.linear_model import LinearRegression

# Set up styles
sns.set_style('whitegrid')
plt.style.use("fivethirtyeight")

# Override yfinance with pandas datareader
yf.pdr_override()

# List of tech stocks for analysis
tech_list = ['AAPL', 'GOOG', 'MSFT', 'AMZN', 'SBUX', 'CSCO', 'META', 'TSLA', 'AMD', 'NFLX']
tech_dict = {
    'Apple': 'AAPL',
    'Google': 'GOOG',
    'Microsoft': 'MSFT',
    'Amazon': 'AMZN',
    'Starbucks': 'SBUX',
    'Cisco': 'CSCO',
    'Meta': 'META',
    'Tesla': 'TSLA',
    'AMD': 'AMD',
    'Netflix': 'NFLX'
}

# Set up End and Start times for data grab
end = datetime.now()
start = datetime(end.year - 3, end.month, end.day)

# Fetch data for each stock and add a Ticker column
company_list = []
for stock in tech_list:
    try:
        data = yf.download(stock, start=start, end=end)
        data['Ticker'] = stock
        company_list.append(data)
    except Exception as e:
        st.error(f"Error downloading data for {stock}: {e}")

# Combine all stocks into a single DataFrame
df = pd.concat(company_list)
df.reset_index(inplace=True)

# Adding moving averages
ma_days = [10, 20, 50]
for ma in ma_days:
    df[f"MA_{ma}"] = df.groupby('Ticker')['Adj Close'].transform(lambda x: x.rolling(ma).mean())

# Feature Engineering: Create features and labels
df['Prediction'] = df.groupby('Ticker')['Adj Close'].shift(-1)

# Drop rows with NaN values
df.dropna(inplace=True)

# Splitting data into training and testing sets
train_data = df[df['Date'] < datetime(2023, 1, 1)]
test_data = df[df['Date'] >= datetime(2023, 1, 1)]

# Prepare the feature set and labels
features = ['Adj Close', 'MA_10', 'MA_20', 'MA_50']
X_train = train_data[features]
y_train = train_data['Prediction']
X_test = test_data[features]
y_test = test_data['Prediction']

# Train a Linear Regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Streamlit interface
st.title('Stock Market Price Prediction')

# Add background image via CSS
background_image_url = 'https://t4.ftcdn.net/jpg/02/98/84/69/240_F_298846909_mssb9MpliUGU22kW0r0i7dMjPwdGMkZy.jpg'  # Replace with your image URL
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url({background_image_url});
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# User inputs
company_name = st.selectbox('Select a company', list(tech_dict.keys()))
selected_date = st.date_input('Select a date', min_value=start.date(), max_value=end.date())

# Process the input date
selected_date = datetime.combine(selected_date, datetime.min.time())

if st.button('Predict'):
    # Fetch the latest data for the selected company
    stock_symbol = tech_dict[company_name]
    try:
        stock_data = yf.download(stock_symbol, start=start, end=end)
        
        # Calculate moving averages for the selected company's data
        for ma in ma_days:
            stock_data[f"MA_{ma}"] = stock_data['Adj Close'].rolling(ma).mean()
        
        # Get the row corresponding to the selected date
        input_data = stock_data.loc[stock_data.index == selected_date]
        
        if not input_data.empty:
            # Prepare the feature set
            input_features = input_data[features]
            
            # Make the prediction
            prediction = model.predict(input_features)
            
            # Display the predicted price
            st.write(f"The predicted stock price for {company_name} on {selected_date.date()} is ${prediction[0]:.2f}")
        else:
            st.write(f"No data available for {selected_date.date()}")
    except Exception as e:
        st.error(f"Error fetching data for prediction: {e}")

# Visualizing the results (optional)
if st.checkbox('Show stock prices over time'):
    plt.figure(figsize=(14, 7))
    sns.lineplot(data=df, x='Date', y='Adj Close', hue='Ticker')
    plt.title('Stock Prices Over Time')
    plt.xlabel('Year')
    plt.ylabel('Closing Price')
    plt.xticks(rotation=45)
    st.pyplot(plt)
 
