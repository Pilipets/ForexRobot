TODO:

Major:
1. Rethink vectorized strategy - maybe async loop and support multiple open positions within the same symbol;
2. Add streaming(without active waiting) example architecture and strategy;
3. Add ML based strategies architecture + implementation - https://github.com/huseinzol05/Stock-Prediction-Models, https://github.com/RaidasGrisk/Trading-Bot;

Minor:
General:
1. Add hosting for strategies on AWS(EC2);
2. Add console running options with configs;

FXCMPY:
1. Report an issue with float position size in the limit order - https://github.com/fxcm/RestAPI/issues;
2. Provide modified fxcmpy libraries until all fixed;

Backtesting:
1. Add more FOREX backtesting;

Portfolio
1. Remove inactive orders from the Portfolio;
2. Resolve the mess with str in BasePortfolio.order_ids, while somewhere int expected, somewhere - str;

Strategy:
1. Add stop_loss, take_profit based on the ATR, deduce pips value from ATR;
2. Add run until opened option;
3. Add some randomizer for the position size;
4. Calculate position based on available margin and risk rate - not points;

BBand:
1. Make stop_loss, take_profit limits as described here - https://github.com/tanvird3/TradingRobot;
GridStrategy:
1. Add better exception handling + logging in iter_run;
2. Implement self.interval_price calculation based on ATR, BBands if not provided;
3. Add moving grid option;