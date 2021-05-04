TODO:

Major:
1. Add Fibonacci retracement strategies;
2. Add strategy backtesting;
3. Add hosting for strategies;
4. Add run until opened option;
5. Add console running options with configs;
6. Modify portolio to get stats for individual symbols;
7. Resolve the mess with str in BasePortfolio.order_ids, while somewhere int expected, somewhere - str;

RenkoMACD:
1. Add stop_loss based on ATR, position size calculation based on the risk amount;
2. Remove inactive trade_ids from the portfolio to avoid unnecessary calculations in group_portfolio_positions;
GridStrategy:
1. Add better exception handling + logging in iter_run;
2. Implement self.interval_price calculation based on ATR, BBands if not provided;
3. Add moving grid option;
4. Add randomizer for position size;
5. Add take_profit, stop_loss limits;