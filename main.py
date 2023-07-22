import csv
import yfinance as yf
import mibian
import time
import pandas as pd

# Function to get options data for a specific symbol
def get_options_data(symbol):
    stock = yf.Ticker(symbol)
    expirations = stock.options
    options_data = {}

    for expiry in expirations:
        options_chain = stock.option_chain(expiry)
        options_data[expiry] = options_chain.calls  # You can also add 'puts' if needed

    return options_data

# Function to calculate option Greeks
def calculate_option_greeks(options_data, stock_price, risk_free_rate):
    greeks_data = []
    for expiry, chain in options_data.items():
        for _, option in chain.iterrows():
            try:
                underlying_price = stock_price
                strike_price = option['strike']
                time_to_expiry = (pd.to_datetime(expiry) - pd.Timestamp.today()).days / 365.0
                implied_volatility = option['impliedVolatility']
                option_type = 'call' if option['contractSymbol'].endswith('C') else 'put'

                option_obj = mibian.BS([underlying_price, strike_price, risk_free_rate, time_to_expiry],
                                       volatility=implied_volatility * 100.0)

                delta = option_obj.callDelta if option_type == 'call' else option_obj.putDelta
                theta = option_obj.callTheta if option_type == 'call' else option_obj.putTheta
                vega = option_obj.vega
                gamma = option_obj.gamma
                rho = option_obj.callRho if option_type == 'call' else option_obj.putRho

                greeks_data.append([option['contractSymbol'], expiry, delta, theta, vega, gamma, rho,
                                    option['lastPrice'], option['openInterest'], option['volume'],
                                    option['bid'], option['ask'], option['change'], option['percentChange']])

            except Exception as e:
                print(f"Error calculating Greeks for {option['contractSymbol']} - {e}")

    return greeks_data

# Function to export options and Greeks to a CSV file
def export_data_to_csv(symbol, options_data, greeks_data, filename):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)

        # Export options and Greeks
        writer.writerow(['Contract Symbol', 'Expiry', 'Delta', 'Theta', 'Vega', 'Gamma', 'Rho',
                         'Last Price', 'Open Interest', 'Volume', 'Bid', 'Ask', 'Change', 'Percent Change'])
        for greek_data in greeks_data:
            writer.writerow(greek_data)

if __name__ == "__main__":
    # List of stock symbols to analyze (replace with your desired list of symbols)
    stock_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

    # Fetch and export options and Greeks data for each symbol
    for symbol in stock_symbols:
        options_data = get_options_data(symbol)
        if options_data:
            # Replace the risk_free_rate with the appropriate value (e.g., 0.02 for 2%)
            risk_free_rate = 0.02
            stock_price = options_data[list(options_data.keys())[0]]['lastPrice'][0]  # Use the first option's last price as stock price
            greeks_data = calculate_option_greeks(options_data, stock_price, risk_free_rate)
            export_data_to_csv(symbol, options_data, greeks_data, f'{symbol}_options_data.csv')
        else:
            print(f"No valid option data for {symbol}")

        time.sleep(10)  # Introduce a delay of 10 seconds between API calls (if needed)

print("Script execution completed.")
