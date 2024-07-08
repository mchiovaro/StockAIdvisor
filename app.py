#%% packages
import yfinance as yf
import anthropic
import panel as pn
import datetime
import os
import matplotlib.pyplot as plt

pn.extension() # this activates chat interface

#%% set client
client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

#%% model params
MODEL = "claude-3-haiku-20240307"
MAX_TOKENS = 1024

#%% pricing function (child)
def get_data(ticker:str, start='2024-01-01', end='2024-06-16'):
    stock_data = yf.download(ticker, start=start, end=end)
    return stock_data

#%% ticker function (child)
def get_ticker(description:str):
    response = client.messages.create(
        
        # set up model
        model=MODEL,
        max_tokens=MAX_TOKENS,

        # define the instructions and properties
        tools=[
            {
                "name": "get_ticker", # name of the func
                "description": "Provide the stock ticker for the most probable company which is described in the input text. If in doubt which company to choose, use the company with the highest market capitalization.",
                "input_schema": {
                    "type": "object",
                    "properties": { # define what properties to define
                        "ticker": {
                            "type": "string",
                            "description": "Ticker symbol of the company, e.g. TSLA",
                        }
                    },
                    "required": ["ticker"],
                },
            }
        ],
        messages=[{"role": "user", "content": description}],
    )
    return response.content[0].input['ticker']

#%% get advanced metrics
def get_adv_metrics(df):
    
    # Calculate daily returns
    df['Daily Return'] = df['Adj Close'].pct_change()
    
    # Calculate average daily return
    avg_daily_return = df['Daily Return'].mean()
    
    # Calculate volatility (standard deviation of returns)
    volatility = df['Daily Return'].std()
    
    # Calculate Sharpe ratio (assumes risk-free rate is 0)
    sharpe_ratio = avg_daily_return / volatility
    
    # Calculate cumulative returns
    df['Cumulative Return'] = (1 + df['Daily Return']).cumprod()
    
    # Calculate maximum drawdown
    rolling_max = df['Cumulative Return'].cummax()
    drawdown = df['Cumulative Return'] / rolling_max - 1
    max_drawdown = drawdown.min()

    return avg_daily_return, volatility, sharpe_ratio, max_drawdown

#%% get plot of performance
def get_year_plot():

    # create figure
    figsize=(20,15)

    try:

        closing_price = df['Adj Close']
        df.reset_index(inplace=True)  
        date = df['Date']

        # create a simple plot 
        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(date, closing_price)
    
        # wrap up
        #ax.set(xlabel ='date', ylabel ='closing price', title = "Stock Value")
        ax.set_xlabel(xlabel ='date', fontsize=25)
        ax.set_ylabel(ylabel ='closing price', fontsize=25)
        ax.set_title(label ='Stock Value', fontsize=40)
        ax.xaxis.set_tick_params(labelsize=20)
    
        #ax.set('date', fontsize = 50)
        plt.close(fig)

    except:
        # generate a blank figure before user has entered prompt
        fig, ax = plt.subplots(figsize=(20, 15))
        ax.axis('off')  # Turn off axis
        ax.set_facecolor('white')  # Set background color to white
        plt.close(fig)

    return fig
#%%
def update_plot():
    # Clear the current plot
    plt.clf()
    # Get the new performance data for the company
    new_plot = get_year_plot()
    # Update the plot pane
    plot.object = new_plot

#%% get stock performance in this year (callback - parent)
def get_performance(question, user, interface):

    # get date and ticker
    current_day = str(datetime.date.today())
    last_year_date = str(f"{datetime.date.today().year-1}-{datetime.date.today().month}-{datetime.date.today().day}")
    ticker = get_ticker(question)

    # get the price info
    global df
    df = get_data(ticker, start=last_year_date, end=current_day)

    # update the plot
    update_plot()
    
    # get basic pricing info
    price_at_beginning_of_last = df["Close"].iloc[0]
    price_recent = df["Close"].iloc[-1]
    performance_since_last_year = (price_recent / price_at_beginning_of_last - 1) * 100

    # get advanced metrics
    avg_daily_return, volatility, sharpe_ratio, max_drawdown = get_adv_metrics(df)

    # clear up memory
    del [df]

    # feed the ticker, price, and performance info to the llm
    message = client.messages.create(
    model=MODEL,
    max_tokens=MAX_TOKENS,
    messages=[
        {
            "role": "user", 
            "content": f"You are a stock analyst and financial advisor. You are considering the company and performance for the stock {ticker}. First, provide an overview of the company. Review how the stock is {performance_since_last_year}% in the last year, starting with {price_at_beginning_of_last} one year ago and the price on {current_day} is {price_recent}. Be sure to list these out in bullet points before evaluating them. Then, evaluate how this year, the average daily return is {avg_daily_return} per day, volatility is {volatility}, Sharpe ratio is {sharpe_ratio}, and Max Drawdown is {max_drawdown}. Be sure to list these out in bullet points before evaluating them. Round everything to one decimal place when reporting. As you review, provide information on if you think investmenting is a good choice, based on risk tolerance. Do not give advice. Let the user know that you are simply providing as assessment and not advice, and that they should consult a financial professional. Explain everything simply, as if talking to someone with little knowledge about investing."}

    ])

    # return the performance eval
    return message.content[0].text

#%% set up chat interface where the call is to get_performance()
chat_interface = pn.chat.ChatInterface(
    callback = get_performance,
    callback_user = "LLM"
)

# add elements to the chat interface (prompt and entry bar/submit button)
chat_interface.send(
    "Describe the company you want to know the stock performance for.",
    user="AI Stock Analyst",
    respond=False
)

# make plot
plot = pn.pane.Matplotlib(get_year_plot(), dpi=44, tight=True)

#put elements together
layout = pn.Row(chat_interface, plot)

# serve
layout.servable()
#layout.show()
# %%
