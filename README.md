---
title: StockAIdvisor
emoji: 💸
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# StockAIdvisor

_An app for stock identification and assessment using Claude._

**StockAIdvisor** is a tool for assessing stocks based on the previous years performance. Users can enter descriptions of the type of company they'd like to invest in. Claude will identify the company that they are most likely referring to (or that with the largest market cap) and return the ticker. The ticker is then used to collect performance data from `yfinance` and calculate various performance metrics. These metrics are then fed to Claude again to evaluate the stock's viability as a current investment choice based on risk tolerance. 

## Instructions
Navigate to the [Stock AIdvisor on Huggingface Spaces](https://huggingface.co/spaces/mchiovaro/stock-aidvisor) to give it a try. 

_This costs $$ to run! Please be mindful of others so that there are enough credits to go around. If there appear to be no more credits, feel free to send a message._

## Contributions
Feel free to submit a pull request for any issues or improvements! \
Author: Megan Chiovaro (@mchiovaro)