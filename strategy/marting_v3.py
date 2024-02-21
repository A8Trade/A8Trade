"""
简单的ema策略
"""
from datetime import datetime
from decimal import Decimal

import talib

from vnpy.app.cta_strategy import BacktestingEngine
from vnpy.app.cta_strategy.template import CtaTemplate
from typing import Any

from vnpy.trader.constant import Direction, Offset
from vnpy.trader.object import BarData, Interval, TradeData
from vnpy.trader.utility import BarGenerator, ArrayManager


class BitquantEmaStrategy(CtaTemplate):
    # 策略的核心参数.
    initial_trading_value = 200  # 首次开仓价值 1000USDT.
    trading_value_multiplier = 2  # 加仓的比例.
    max_increase_pos_count = 5  # 最大的加仓次数

    hour_pump_pct = 0.026  # 小时的上涨百分比
    four_hour_pump_pct = 0.046  # 四小时的上涨百分比.
    high_close_change_pct = 0.03  # 最高价/收盘价 -1, 防止上引线过长.
    increase_pos_when_dump_pct = 0.05  # 价格下跌 5%就继续加仓.
    exit_profit_pct = 0.01  # 出场平仓百分比 1%
    exit_pull_back_pct = 0.01  # 最高价回调超过1%，且利润超过1% 就出场.
    trading_fee = 0.00075  # 交易手续费

    # 变量
    avg_price = 0.0  # 当前持仓的平均价格.
    last_entry_price = 0.0  # 上一次入场的价格.
    entry_highest_price = 0.0
    current_pos = 0.0  # 当前的持仓的数量.
    current_increase_pos_count = 0  # 当前的加仓的次数.
    total_profit = 0  # 统计总的利润.

    parameters = ["initial_trading_value", "trading_value_multiplier", "max_increase_pos_count",
                  "hour_pump_pct", "four_hour_pump_pct", "high_close_change_pct", "increase_pos_when_dump_pct",
                  "exit_profit_pct",
                  "exit_pull_back_pct", "trading_fee"]

    variables = ["avg_price", "last_entry_price", "entry_highest_price", "current_pos", "current_increase_pos_count",
                 "total_profit"]

    def __init__(
            self,
            cta_engine: Any,
            strategy_name: str,
            vt_symbol: str,
            setting: dict, ):
        super(BitquantEmaStrategy, self).__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.am = ArrayManager(200)

        self.bg_1hour = BarGenerator(self.on_bar, 1, on_window_bar=self.on_1hour_bar, interval=Interval.HOUR)  # 1hour
        self.bg_4hour = BarGenerator(self.on_bar, 4, on_window_bar=self.on_4hour_bar, interval=Interval.HOUR)  # 4hour

        # self.cta_engine.event_engine.register(EVENT_ACCOUNT + 'BINANCE.币名称', self.process_acccount_event)
        # self.cta_engine.event_engine.register(EVENT_ACCOUNT + "BINANCE.USDT", self.process_account_event)

        self.buy_orders = []  # 买单id列表。
        self.sell_orders = []  # 卖单id列表。
        self.min_notional = 11  # 最小的交易金额.

    def on_bar(self, bar: BarData):
        """
                Callback of new bar data update.
                """
        if self.entry_highest_price > 0:
            self.entry_highest_price = max(bar.high_price, self.entry_highest_price)

        if self.current_pos * bar.close_price >= self.min_notional:

            if len(self.sell_orders) <= 0 < self.avg_price:
                # 有利润平仓的时候
                # 清理掉其他买单.

                profit_percent = bar.close_price / self.avg_price - 1
                profit_pull_back_pct = self.entry_highest_price / bar.close_price - 1
                if profit_percent >= self.exit_profit_pct and profit_pull_back_pct >= self.exit_pull_back_pct:
                    self.cancel_all()
                    orderids = self.sell(bar.close_price, abs(self.current_pos))
                    self.sell_orders.extend(orderids)

            if len(self.buy_orders) <= 0:
                # 考虑加仓的条件: 1） 当前有仓位,且仓位值要大于11USDTyi以上，2）加仓的次数小于最大的加仓次数，3）当前的价格比上次入场的价格跌了一定的百分比。

                dump_down_pct = self.last_entry_price / bar.close_price - 1

                if self.current_increase_pos_count <= self.max_increase_pos_count and dump_down_pct >= self.increase_pos_when_dump_pct:
                    # ** 表示的是乘方.
                    self.cancel_all()  # 清理其他卖单.

                    increase_pos_value = self.initial_trading_value * self.trading_value_multiplier ** self.current_increase_pos_count
                    price = bar.close_price
                    vol = increase_pos_value / price
                    orderids = self.buy(price, vol)
                    self.buy_orders.extend(orderids)

        self.bg_1hour.update_bar(bar)
        self.bg_4hour.update_bar(bar)

    def on_5min_bar(self, bar: BarData):
        print(bar)

    def on_4hour_bar(self, bar: BarData):
        close_change_pct = bar.close_price / bar.open_price - 1  # 收盘价涨了多少.
        high_change_pct = bar.high_price / bar.close_price - 1  # 计算上引线

        # 回调一定比例的时候.
        if self.current_pos * bar.close_price < self.min_notional:
            # 每次下单要大于等于10USDT, 为了简单设置11USDT.
            if close_change_pct >= self.four_hour_pump_pct and high_change_pct < self.high_close_change_pct and len(
                    self.buy_orders) == 0:
                # 这里没有仓位.
                # 重置当前的数据.
                self.cancel_all()
                self.current_increase_pos_count = 0
                self.avg_price = 0
                self.entry_highest_price = 0.0

                price = bar.close_price
                vol = self.initial_trading_value / price
                orderids = self.buy(price, vol)
                self.buy_orders.extend(orderids)  # 以及已经下单的orderids.


    def on_1hour_bar(self, bar: BarData):
        close_change_pct = bar.close_price / bar.open_price - 1  # 收盘价涨了多少.
        high_change_pct = bar.high_price / bar.close_price - 1  # 计算上引线

        # 回调一定比例的时候.
        if self.current_pos * bar.close_price < self.min_notional:
            # 每次下单要大于等于10USDT, 为了简单设置11USDT.
            if close_change_pct >= self.hour_pump_pct and high_change_pct < self.high_close_change_pct and len(
                    self.buy_orders) == 0:
                # 这里没有仓位.
                # 重置当前的数据.
                self.cancel_all()
                self.current_increase_pos_count = 0
                self.avg_price = 0
                self.entry_highest_price = 0.0

                price = bar.close_price
                vol = self.initial_trading_value / price
                orderids = self.buy(price, vol)
                self.buy_orders.extend(orderids)  # 以及已经下单的orderids.


    def on_init(self):
        print("on init")
        '''
            加载三天数据
        '''
        self.load_bar(3)

    def on_trade(self, trade: TradeData):
        """
               Callback of new trade data update.
               """
        if trade.direction == Direction.LONG:
            total = self.avg_price * self.current_pos + float(trade.price) * float(trade.volume)
            self.current_pos += float(trade.volume)

            self.avg_price = total / self.current_pos
        elif trade.direction == Direction.SHORT:
            self.current_pos -= float(trade.volume)

            # 计算统计下总体的利润.
            profit = (float(trade.price) - self.avg_price) * float(trade.volume)
            total_fee = float(trade.volume) * float(trade.price) * 2 * self.trading_fee
            self.total_profit += profit - total_fee

if __name__ == '__main__':
    engine = BacktestingEngine()

    engine.set_parameters(
        vt_symbol="UNFIUSDT.BINANCE",
        # 分钟级别
        interval=Interval.MINUTE,
        start=datetime(2017, 1, 1),
        # 费率
        rate=7.5 / 10000,
        # 滑点
        slippage=0.5,

        size=1,

        # 价差
        pricetick=0.5,

        # 初始参数
        capital=1000,

        end=datetime(2022, 8, 19)
    )

    engine.add_strategy(BitquantEmaStrategy, {})
    engine.load_data()
    engine.run_backtesting()
    engine.calculate_result()
    engine.calculate_statistics()
    engine.show_chart()

