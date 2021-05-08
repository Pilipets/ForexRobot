TODO:

Major:
1. Add strategy backtesting - https://kernc.github.io/backtesting.py/;
2. Add hosting for strategies(AWS, EC2);
3. Add console running options with configs;
4. Rethink vectorized strategy - maybe async loop and support multiple open positions within same symbol;
5. Provide modified fxcmpy libraries;	

Minor:
Portfolio
1. Remove inactive orders from the Portfolio;
2. Resolve the mess with str in BasePortfolio.order_ids, while somewhere int expected, somewhere - str;

Strategy:
1. Add stop_loss, take_profit based on the ATR;
2. Add run until opened option;
3. Add ML based strategies architecture + implementation - https://github.com/huseinzol05/Stock-Prediction-Models, https://github.com/RaidasGrisk/Trading-Bot;
BBand:
1. Make stop_loss, take_profit limits as described here - https://github.com/tanvird3/TradingRobot;
GridStrategy:
1. Add better exception handling + logging in iter_run;
2. Implement self.interval_price calculation based on ATR, BBands if not provided;
3. Add moving grid option;
4. Add randomizer for position size;