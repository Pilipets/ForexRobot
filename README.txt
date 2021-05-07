TODO:

Major:
1. Add BBandMACD strategy - https://github.com/tanvird3/TradingRobot;
2. Rethink vectorized strategy and portfolio - maybe for one symbol and async loop?
Rethink pos_size;
3. Add strategy backtesting - https://kernc.github.io/backtesting.py/;
4. Add hosting for strategies; (AWS, EC2)
5. Add run until opened option;
6. Add console running options with configs;
7. Add Fibonacci retracement strategies;
8. Resolve the mess with str in BasePortfolio.order_ids, while somewhere int expected, somewhere - str;

RenkoMACD:
1. Add stop_loss based on ATR, position size calculation based on the risk amount;
2. Remove inactive trade_ids from the portfolio to avoid unnecessary calculations in group_portfolio_positions;
GridStrategy:
1. Add better exception handling + logging in iter_run;
2. Implement self.interval_price calculation based on ATR, BBands if not provided;
3. Add moving grid option;
4. Add randomizer for position size;
5. Add take_profit, stop_loss limits;