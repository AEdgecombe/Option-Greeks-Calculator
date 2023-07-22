import yfinance as yf
import mibian
import pandas as pd
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QFont


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
                messagebox.showerror("Error", f"Error calculating Greeks for {option['contractSymbol']} - {str(e)}")

    return greeks_data

def submit():
    symbol = line_edit.text().upper()
    text_edit.append(f'Stock ticker: {symbol}\n')

    options_data = get_options_data(symbol)
    if options_data:
        # Replace the risk_free_rate with the appropriate value (e.g., 0.02 for 2%)
        risk_free_rate = 0.02
        stock_price = options_data[list(options_data.keys())[0]]['lastPrice'][0]  # Use the first option's last price as stock price
        greeks_data = calculate_option_greeks(options_data, stock_price, risk_free_rate)

        table.setRowCount(0)  # clear the table
        for row_data in greeks_data:
            row_number = table.rowCount()
            table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        text_edit.append("Data fetched and displayed.\n")
    else:
        text_edit.append(f"No valid option data for {symbol}\n")

app = QApplication([])
stylesheet ="""QToolTip
{
     border: 2px solid #121212;
     background-color: #ffb13f;
     padding: 2px;
     border-radius: 4px;
     opacity: 100;
}

QWidget
{
    color: #c1c1c1;
    background-color: #333333;
}

QTreeView, QListView
{
    background-color: #b0b0b0;
    margin-left: 6px;
}

QWidget:item:hover
{
    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffb13f, stop: 1 #cb0719);
    color: #010101;
}

QWidget:item:selected
{
    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffb13f, stop: 1 #d88a1b);
}

QMenuBar::item
{
    background: transparent;
}

QMenuBar::item:selected
{
    background: transparent;
    border: 2px solid #ffbb00;
}

QMenuBar::item:pressed
{
    background: #555;
    border: 2px solid #111;
    background-color: QLinearGradient(
        x1:0, y1:0,
        x2:0, y2:1,
        stop:1 #313131,
        stop:0.5 #444444
    );
    margin-bottom:-2px;
    padding-bottom:2px;
}

QMenu
{
    border: 2px solid #111;
}

QMenu::item
{
    padding: 3px 21px 3px 21px;
}

QMenu::item:selected
{
    color: #010101;
}

QWidget:disabled
{
    color: #909090;
    background-color: #333333;
}

QAbstractItemView
{
    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #5e5e5e, stop: 0.1 #757575, stop: 1 #6e6e6e);
}

QWidget:focus
{
    /*border: 2px solid gray;*/
}

QLineEdit
{
    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #5e5e5e, stop: 0 #757575, stop: 1 #6e6e6e);
    padding: 2px;
    border-style: solid;
    border: 2px solid #2f2f2f;
    border-radius: 6;
}

QPushButton
{
    color: #c1c1c1;
    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #676767, stop: 0.1 #636363, stop: 0.5 #5f5f5f, stop: 0.9 #5b5b5b, stop: 1 #575757);
    border-width: 2px;
    border-color: #2f2f2f;
    border-style: solid;
    border-radius: 7;
    padding: 4px;
    font-size: 13px;
    padding-left: 6px;
    padding-right: 6px;
    min-width: 41px;
}

QPushButton:pressed
{
    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #3e3e3e, stop: 0.1 #3c3c3c, stop: 0.5 #393939, stop: 0.9 #383838, stop: 1 #363636);
}

QComboBox
{
    selection-background-color: #ffbb00;
    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #676767, stop: 0.1 #636363, stop: 0.5 #5f5f5f, stop: 0.9 #5b5b5b, stop: 1 #575757);
    border-style: solid;
    border: 2px solid #2f2f2f;
    border-radius: 6;
}

QComboBox:hover,QPushButton:hover
{
    border: 3px solid QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffb13f, stop: 1 #d88a1b);
}

QComboBox:on
{
    padding-top: 4px;
    padding-left: 5px;
    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #3e3e3e, stop: 0.1 #3c3c3c, stop: 0.5 #393939, stop: 0.9 #383838, stop: 1 #363636);
    selection-background-color: #ffbb00;
}

QComboBox QAbstractItemView
{
    border: 3px solid gray;
    selection-background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffb13f, stop: 1 #d88a1b);
}

QComboBox::drop-down
{
     subcontrol-origin: padding;
     subcontrol-position: top right;
     width: 16px;

     border-left-width: 0px;
     border-left-color: gray;
     border-left-style: solid; /* just a single line */
     border-top-right-radius: 4px; /* same radius as the QComboBox */
     border-bottom-right-radius: 4px;
 }

QComboBox::down-arrow
{
     image: url(:/dark_orange/img/down_arrow.png);
}

QGroupBox
{
    border: 2px solid gray;
    margin-top: 11px;
}

QGroupBox:focus
{
    border: 2px solid gray;
}

QTextEdit:focus
{
    border: 2px solid gray;
}

QScrollBar:horizontal {
     border: 2px solid #333333;
     background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0.0 #232323, stop: 0.2 #393939, stop: 1 #595959);
     height: 8px;
     margin: 0px 17px 0 17px;
}

QScrollBar::handle:horizontal
{
      background: QLinearGradient( x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #ffb13f, stop: 0.5 #d88a1b, stop: 1 #ffb13f);
      min-height: 21px;
      border-radius: 3px;
}

QScrollBar::add-line:horizontal {
      border: 2px solid #2b2b2b;
      border-radius: 3px;
      background: QLinearGradient( x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #ffb13f, stop: 1 #d88a1b);
      width: 15px;
      subcontrol-position: right;
      subcontrol-origin: margin;
}

QScrollBar::sub-line:horizontal {
      border: 2px solid #2b2b2b;
      border-radius: 3px;
      background: QLinearGradient( x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #ffb13f, stop: 1 #d88a1b);
      width: 15px;
     subcontrol-position: left;
     subcontrol-origin: margin;
}

QScrollBar::right-arrow:horizontal, QScrollBar::left-arrow:horizontal
{
      border: 2px solid black;
      width: 2px;
      height: 2px;
      background: #f0f0f0;
}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal
{
      background: none;
}

QScrollBar:vertical
{
      background: QLinearGradient( x1: 0, y1: 0, x2: 1, y2: 0, stop: 0.0 #232323, stop: 0.2 #393939, stop: 1 #595959);
      width: 8px;
      margin: 17px 0 17px 0;
      border: 2px solid #333333;
}

QScrollBar::handle:vertical
{
      background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffb13f, stop: 0.5 #d88a1b, stop: 1 #ffb13f);
      min-height: 21px;
      border-radius: 3px;
}

QScrollBar::add-line:vertical
{
      border: 2px solid #2b2b2b;
      border-radius: 3px;
      background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffb13f, stop: 1 #d88a1b);
      height: 15px;
      subcontrol-position: bottom;
      subcontrol-origin: margin;
}

QScrollBar::sub-line:vertical
{
      border: 2px solid #2b2b2b;
      border-radius: 3px;
      background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #d88a1b, stop: 1 #ffb13f);
      height: 15px;
      subcontrol-position: top;
      subcontrol-origin: margin;
}

QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical
{
      border: 2px solid black;
      width: 2px;
      height: 2px;
      background: #f0f0f0;
}


QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical
{
      background: none;
}

QTextEdit
{
    background-color: #353535;
}

QPlainTextEdit
{
    background-color: #353535;
}

QHeaderView::section
{
    background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #727272, stop: 0.5 #606060, stop: 0.6 #545454, stop:1 #767676);
    color: #f0f0f0;
    padding-left: 5px;
    border: 2px solid #7c7c7c;
}

QCheckBox:disabled
{
color: #515151;
}

QDockWidget::title
{
    text-align: center;
    spacing: 4px; /* spacing between items in the tool bar */
    background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #434343, stop: 0.5 #343434, stop:1 #434343);
}

QDockWidget::close-button, QDockWidget::float-button
{
    text-align: center;
    spacing: 2px; /* spacing between items in the tool bar */
    background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #434343, stop: 0.5 #343434, stop:1 #434343);
}

QDockWidget::close-button:hover, QDockWidget::float-button:hover
{
    background: #343434;
}

QDockWidget::close-button:pressed, QDockWidget::float-button:pressed
{
    padding: 2px -2px -2px 2px;
}

QMainWindow::separator
{
    background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #262626, stop: 0.5 #252525, stop: 0.6 #313131, stop:1 #444444);
    color: #f0f0f0;
    padding-left: 5px;
    border: 2px solid #5c5c5c;
    spacing: 4px; /* spacing between items in the tool bar */
}

QMainWindow::separator:hover
{

    background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d88a1b, stop:0.5 #c46d17 stop:1 #ffb13f);
    color: #f0f0f0;
    padding-left: 5px;
    border: 2px solid #7c7c7c;
    spacing: 4px; /* spacing between items in the tool bar */
}

QToolBar::handle
{
     spacing: 4px; /* spacing between items in the tool bar */
     background: url(:/dark_orange/img/handle.png);
}

QMenu::separator
{
    height: 3px;
    background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #262626, stop: 0.5 #252525, stop: 0.6 #313131, stop:1 #444444);
    color: #f0f0f0;
    padding-left: 5px;
    margin-left: 11px;
    margin-right: 6px;
}

QProgressBar
{
    border: 3px solid #808080;
    border-radius: 6px;
    text-align: center;
}

QProgressBar::chunk
{
    background-color: #d88a1b;
    width: 2.35px;
    margin: 0.55px;
}

QTabBar::tab {
    color: #c2c2c2;
    border: 2px solid #555;
    border-bottom-style: none;
    background-color: #434343;
    padding-left: 11px;
    padding-right: 11px;
    padding-top: 4px;
    padding-bottom: 3px;
    margin-right: -2px;
}

QTabWidget::pane {
    border: 2px solid #555;
    top: 2px;
}

QTabBar::tab:last
{
    margin-right: 0; /* the last selected tab has nothing to overlap with on the right */
    border-top-right-radius: 4px;
}

QTabBar::tab:first:!selected
{
 margin-left: 0px; /* the last selected tab has nothing to overlap with on the right */


    border-top-left-radius: 4px;
}

QTabBar::tab:!selected
{
    color: #c2c2c2;
    border-bottom-style: solid;
    margin-top: 4px;
    background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:1 #313131, stop:.4 #444444);
}

QTabBar::tab:selected
{
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-bottom: 0px;
}

QTabBar::tab:!selected:hover
{
    /*border-top: 2px solid #ffaa00;
    padding-bottom: 3px;*/
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:1 #313131, stop:0.4 #444444, stop:0.2 #444444, stop:0.1 #ffb13f);
}

QRadioButton::indicator:checked, QRadioButton::indicator:unchecked{
    color: #c2c2c2;
    background-color: #434343;
    border: 2px solid #c2c2c2;
    border-radius: 7px;
}

QRadioButton::indicator:checked
{
    background-color: qradialgradient(
        cx: 0.5, cy: 0.5,
        fx: 0.5, fy: 0.5,
        radius: 1.0,
        stop: 0.25 #ffb13f,
        stop: 0.3 #434343
    );
}

QCheckBox::indicator{
    color: #c2c2c2;
    background-color: #434343;
    border: 2px solid #c2c2c2;
    width: 10px;
    height: 10px;
}

QRadioButton::indicator
{
    border-radius: 7px;
}

QRadioButton::indicator:hover, QCheckBox::indicator:hover
{
    border: 2px solid #ffb13f;
}

QCheckBox::indicator:checked
{
    image:url(:/dark_orange/img/checkbox.png);
}

QCheckBox::indicator:disabled, QRadioButton::indicator:disabled
{
    border: 2px solid #555;
}


QSlider::groove:horizontal {
    border: 2px solid #4A4949;
    height: 9px;
    background: #302F2F;
    margin: 3px 0;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1,
      stop: 0.0 #b0b0b0, stop: 0.2 #b8b8b8, stop: 1 #888888);
    border: 2px solid #4A4949;
    width: 15px;
    height: 15px;
    margin: -5px 0;
    border-radius: 3px;
}

QSlider::groove:vertical {
    border: 2px solid #4A4949;
    width: 9px;
    background: #302F2F;
    margin: 0 3px;
    border-radius: 3px;
}

QSlider::handle:vertical {
    background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0.0 #b0b0b0,
      stop: 0.2 #b8b8b8, stop: 1 #888888);
    border: 2px solid #4A4949;
    width: 15px;
    height: 15px;
    margin: 0 -5px;
    border-radius: 3px;
}

QAbstractSpinBox {
    padding-top: 3px;
    padding-bottom: 3px;
    border: 2px solid #808080;

    border-radius: 3px;
    min-width: 55px;
}""" 

app.setStyleSheet(stylesheet)

window = QWidget()
window.setWindowTitle("Options Data")
layout = QVBoxLayout()
window.showMaximized()

line_edit = QLineEdit()
line_edit.textChanged.connect(lambda: line_edit.setText(line_edit.text().upper()))  # Convert input to uppercase as it's typed
layout.addWidget(line_edit)

button = QPushButton("Fetch Options Data")
button.clicked.connect(submit)
button.setDefault(True)  
layout.addWidget(button)

text_edit = QTextEdit()
text_edit.setReadOnly(True)  # Make the text_edit read-only
text_edit.setMaximumHeight(100)  # Set maximum height to make it smaller
layout.addWidget(text_edit)

table = QTableWidget(0, 14)
table.setHorizontalHeaderLabels(['Contract Symbol', 'Expiry', 'Delta', 'Theta', 'Vega', 'Gamma', 'Rho', 'Last Price', 'Open Interest', 'Volume', 'Bid', 'Ask', 'Change', 'Percent Change'])
table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
layout.addWidget(table)

window.setLayout(layout)

window.show()

sys.exit(app.exec_())

