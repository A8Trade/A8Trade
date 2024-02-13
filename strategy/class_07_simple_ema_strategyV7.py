"""
    简单EMA策略.

"""
import pandas as pd
import talib
from vnpy.app.cta_strategy.template import CtaTemplate
from typing import Any

from vnpy.trader.constant import Direction, Offset
from vnpy.trader.object import BarData, Interval, TickData, TradeData
from vnpy.trader.utility import BarGenerator
from datetime import datetime
from vnpy.app.cta_strategy.backtesting import BacktestingEngine
from vnpy.app.cta_strategy.base import StopOrder


class BitquantEmaStrategy(CtaTemplate):
    parameters = ["short_ema", "long_ema", "trade_money", "rsi_window"]
    variables = ['short_ema_values', 'long_ema_values']

    fast_ema_window = 12

    slow_ema_window = 26

    rsi_window = 14

    # 当前的持仓的数量
    current_pos = 0.0

    # 交易的钱
    trade_money = 1000

    total = 0

    long_entry_price = 0.0
    # 1阶段盈损
    short_entry_price = 0.0

    # 一阶段, 止盈变成进场价
    first_phase_price = 0.01

    # 二阶段, 止盈变成0.002
    second_phase_price = 0.02

    # 三阶段，方向信号止盈，
    third_phase_price = 0.03

    def __init__(
            self,
            cta_engine: Any,
            strategy_name: str,
            vt_symbol: str,
            setting: dict):
        super(BitquantEmaStrategy, self).__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg3min = BarGenerator(self.on_bar, window=3, on_window_bar=self.on_3min_bar, interval=Interval.MINUTE)
        self.bg5min = BarGenerator(self.on_bar, window=5, on_window_bar=self.on_5min_bar, interval=Interval.MINUTE)
        self.bg15min = BarGenerator(self.on_bar, window=15, on_window_bar=self.on_15min_bar, interval=Interval.MINUTE)
        self.bg30min = BarGenerator(self.on_bar, window=30, on_window_bar=self.on_30min_bar, interval=Interval.MINUTE)
        self.bg45min = BarGenerator(self.on_bar, window=45, on_window_bar=self.on_45min_bar, interval=Interval.MINUTE)
        self.bg1h = BarGenerator(self.on_bar, window=1, on_window_bar=self.on_1h_bar, interval=Interval.HOUR)
        self.bg2h = BarGenerator(self.on_bar, window=1, on_window_bar=self.on_2h_bar, interval=Interval.HOUR)
        self.bg3h = BarGenerator(self.on_bar, window=1, on_window_bar=self.on_3h_bar, interval=Interval.HOUR)
        self.bg4h = BarGenerator(self.on_bar, window=4, on_window_bar=self.on_4h_bar, interval=Interval.HOUR)
        self.bg8h = BarGenerator(self.on_bar, window=8, on_window_bar=self.on_8h_bar, interval=Interval.HOUR)
        self.bg12h = BarGenerator(self.on_bar, window=12, on_window_bar=self.on_12h_bar, interval=Interval.HOUR)
        self.bg1d = BarGenerator(self.on_bar, window=1, on_window_bar=self.on_1d_bar, interval=Interval.DAILY)
        self.bg1w = BarGenerator(self.on_bar, window=1, on_window_bar=self.on_1w_bar, interval=Interval.WEEKLY)

        # 记录指标
        self.df3min = pd.DataFrame(columns={"open_time": 0, 'open': 1, 'high': 2, 'low': 3, 'close': 4,
                                            'volume': 5, 'close_time': 6, 'trade_money': 7, 'trade_count': 8,
                                            'buy_volume': 9, 'sell_volume': 10, 'other': 11, 'macd': 12,
                                            'rsi_divergence_signal': 13, 'macd_divergence_signal': 14,
                                            'td_sequential': 15
                                            })

        self.df5min = pd.DataFrame(columns={"open_time": 0, 'open': 1, 'high': 2, 'low': 3, 'close': 4,
                                            'volume': 5, 'close_time': 6, 'trade_money': 7, 'trade_count': 8,
                                            'buy_volume': 9, 'sell_volume': 10, 'other': 11, 'macd': 12,
                                            'rsi_divergence_signal': 13, 'macd_divergence_signal': 14,
                                            'td_sequential': 15
                                            })
        self.df15min = pd.DataFrame(columns={"open_time": 0, 'open': 1, 'high': 2, 'low': 3, 'close': 4,
                                             'volume': 5, 'close_time': 6, 'trade_money': 7, 'trade_count': 8,
                                             'buy_volume': 9, 'sell_volume': 10, 'other': 11, 'macd': 12,
                                             'rsi_divergence_signal': 13, 'macd_divergence_signal': 14,
                                             'td_sequential': 15
                                             })

        self.df30min = pd.DataFrame(columns={"open_time": 0, 'open': 1, 'high': 2, 'low': 3, 'close': 4,
                                             'volume': 5, 'close_time': 6, 'trade_money': 7, 'trade_count': 8,
                                             'buy_volume': 9, 'sell_volume': 10, 'other': 11, 'macd': 12,
                                             'rsi_divergence_signal': 13, 'macd_divergence_signal': 14,
                                             'td_sequential': 15
                                             })

        self.df45min = pd.DataFrame(columns={"open_time": 0, 'open': 1, 'high': 2, 'low': 3, 'close': 4,
                                             'volume': 5, 'close_time': 6, 'trade_money': 7, 'trade_count': 8,
                                             'buy_volume': 9, 'sell_volume': 10, 'other': 11, 'macd': 12,
                                             'rsi_divergence_signal': 13, 'macd_divergence_signal': 14,
                                             'td_sequential': 15
                                             })

        self.df1h = pd.DataFrame(columns={"open_time": 0, 'open': 1, 'high': 2, 'low': 3, 'close': 4,
                                          'volume': 5, 'close_time': 6, 'trade_money': 7, 'trade_count': 8,
                                          'buy_volume': 9, 'sell_volume': 10, 'other': 11, 'macd': 12,
                                          'rsi_divergence_signal': 13, 'macd_divergence_signal': 14,
                                          'td_sequential': 15
                                          })
        self.df2h = pd.DataFrame(columns={"open_time": 0, 'open': 1, 'high': 2, 'low': 3, 'close': 4,
                                          'volume': 5, 'close_time': 6, 'trade_money': 7, 'trade_count': 8,
                                          'buy_volume': 9, 'sell_volume': 10, 'other': 11, 'macd': 12,
                                          'rsi_divergence_signal': 13, 'macd_divergence_signal': 14,
                                          'td_sequential': 15
                                          })

        self.df3h = pd.DataFrame(columns={"open_time": 0, 'open': 1, 'high': 2, 'low': 3, 'close': 4,
                                          'volume': 5, 'close_time': 6, 'trade_money': 7, 'trade_count': 8,
                                          'buy_volume': 9, 'sell_volume': 10, 'other': 11, 'macd': 12,
                                          'rsi_divergence_signal': 13, 'macd_divergence_signal': 14,
                                          'td_sequential': 15
                                          })

        self.df4h = pd.DataFrame(columns={"open_time": 0, 'open': 1, 'high': 2, 'low': 3, 'close': 4,
                                          'volume': 5, 'close_time': 6, 'trade_money': 7, 'trade_count': 8,
                                          'buy_volume': 9, 'sell_volume': 10, 'other': 11, 'macd': 12,
                                          'rsi_divergence_signal': 13, 'macd_divergence_signal': 14,
                                          'td_sequential': 15
                                          })

        self.df8h = pd.DataFrame(columns={"open_time": 0, 'open': 1, 'high': 2, 'low': 3, 'close': 4,
                                          'volume': 5, 'close_time': 6, 'trade_money': 7, 'trade_count': 8,
                                          'buy_volume': 9, 'sell_volume': 10, 'other': 11, 'macd': 12,
                                          'rsi_divergence_signal': 13, 'macd_divergence_signal': 14,
                                          'td_sequential': 15
                                          })
        self.df12h = pd.DataFrame(columns={"open_time": 0, 'open': 1, 'high': 2, 'low': 3, 'close': 4,
                                          'volume': 5, 'close_time': 6, 'trade_money': 7, 'trade_count': 8,
                                          'buy_volume': 9, 'sell_volume': 10, 'other': 11, 'macd': 12,
                                          'rsi_divergence_signal': 13, 'macd_divergence_signal': 14,
                                          'td_sequential': 15
                                          })
        self.df1d = pd.DataFrame(columns={"open_time": 0, 'open': 1, 'high': 2, 'low': 3, 'close': 4,
                                          'volume': 5, 'close_time': 6, 'trade_money': 7, 'trade_count': 8,
                                          'buy_volume': 9, 'sell_volume': 10, 'other': 11, 'macd': 12,
                                          'rsi_divergence_signal': 13, 'macd_divergence_signal': 14,
                                          'td_sequential': 15
                                          })

        self.df1w = pd.DataFrame(columns={"open_time": 0, 'open': 1, 'high': 2, 'low': 3, 'close': 4,
                                          'volume': 5, 'close_time': 6, 'trade_money': 7, 'trade_count': 8,
                                          'buy_volume': 9, 'sell_volume': 10, 'other': 11, 'macd': 12,
                                          'rsi_divergence_signal': 13, 'macd_divergence_signal': 14,
                                          'td_sequential': 15
                                          })

    def on_init(self):
        print("on init")
        self.load_bar(3)
        print("init success！")

    def on_start(self):
        """
        Callback when strategy is started.
        """
        print("on_start strategy")

    def on_tick(self, tick: TickData):
        print(tick)
        pass

    def on_bar(self, bar: BarData):

        self.bg3min.update_bar(bar)
        self.bg5min.update_bar(bar)
        self.bg15min.update_bar(bar)
        self.bg45min.update_bar(bar)
        # self.bg1h.update_bar(bar)
        # self.bg2h.update_bar(bar)
        # self.bg3h.update_bar(bar)
        # self.bg4h.update_bar(bar)
        # self.bg8h.update_bar(bar)
        # self.bg12h.update_bar(bar)
        # self.bg1w.update_bar(bar)
        # 如果盈利大于1%，止损放到0.2%

        # 如果利润小于2% 发生 反向信号全部止盈

        # 如果利润大于2% 遇到 反向信号部分止盈利 20%

        # 如果利润大于 10% ， 50% 止盈利

        # 如果利润大于 15% ， 50% 止盈利

        # td9 全部止盈利

        # self.bg1d.update_bar(bar)

    def on_trade(self, trade: TradeData):
        if self.pos != 0:
            if trade.direction == Direction.LONG and trade.offset == Offset.OPEN:
                self.long_entry = trade.price
            elif trade.direction == Direction.SHORT and trade.offset == Offset.OPEN:
                self.short_entry = trade.price
            elif trade.offset == Offset.CLOSE:
                pass

    def on_stop_order(self, stop_order: StopOrder):
        # print(f"on_stop_order{stop_order}")
        pass

    def on_3min_bar(self, bar: BarData):
        new_row = {"open_time": bar.datetime,
                   'open': bar.open_price,
                   'high': bar.high_price,
                   'low': bar.low_price,
                   'close': bar.close_price,
                   'volume': bar.volume,
                   }
        self.df3min = self.df3min.append(new_row, ignore_index=True)
        self.df3min['macd'], self.df3min['macdsignal'], self.df3min['macdhist'] = talib.MACD(self.df3min['close'],
                                                                                             self.fast_ema_window,
                                                                                             self.slow_ema_window, 9)
        # rsi
        self.df3min['rsi'] = talib.RSI(self.df3min['close'], timeperiod=14)

        # 目前macd高度
        current_macdhist = len(self.df3min) - 2
        countMacdhistLessThan = 0
        countMacdhistBigThan = 0
        trend_confirm_count = 1
        trend_confirm_value = 0
        # 检查 MACD 能量柱子是否三次递增或递减
        is_increasing = self.df3min['macdhist'].gt(0).tail(3).all()
        is_decreasing = self.df3min['macdhist'].lt(0).tail(3).all()

        # 计算趋势
        for i in range(current_macdhist - 2, max(current_macdhist - 60, 1), -1):
            # todo 避免左侧
            if self.df3min['macdhist'].iloc[i] > 0:
                countMacdhistBigThan = countMacdhistBigThan + 1
            else:
                countMacdhistLessThan = countMacdhistLessThan - 1
            if (  # 背离信号
                    (self.df3min['close'].iloc[current_macdhist] > self.df3min['close'].iloc[i - 1]) and
                    # 背离信号
                    (self.df3min['rsi'].iloc[current_macdhist] < self.df3min['rsi'].iloc[i - 1]) and
                    # 确认偏离过于确认
                    (self.df3min['rsi'].iloc[i - 1] >= 70 and self.df3min['rsi'].iloc[current_macdhist] >= 70) and
                    # 避免入场机会过于偏离
                    self.df3min['close'].iloc[current_macdhist] > self.df3min['close'].iloc[current_macdhist + 1] > (
                    1 - 0.001) * self.df3min['close'].iloc[current_macdhist] and
                    # 确认下降趋势
                    self.df3min['macdhist'].iloc[current_macdhist] > self.df3min['macdhist'].iloc[
                current_macdhist + 1] >= 0 and
                    # 极大值背离
                    (
                            self.df3min['close'].iloc[i] > self.df3min['close'].iloc[i - 1] and
                            self.df3min['close'].iloc[i] > self.df3min['close'].iloc[i - 2] and
                            self.df3min['close'].iloc[i] > self.df3min['close'].iloc[i - 3] and
                            self.df3min['close'].iloc[i] > self.df3min['close'].iloc[i + 1] and
                            self.df3min['close'].iloc[i] > self.df3min['close'].iloc[i + 2] and
                            self.df3min['close'].iloc[i] > self.df3min['close'].iloc[i + 3]
                    ) and
                    # 避免过于左侧。
                    countMacdhistLessThan <= -3 and
                    is_increasing
                    # 避免过于macd左侧
            ):
                self.df3min['rsi_divergence_signal'].iloc[current_macdhist] = -1  # 1表示存在背离
                print(
                    f"3min, dateTime:{self.df3min['open_time'].iloc[current_macdhist]},close_price:{self.df3min['close'].iloc[current_macdhist]}, dateTime:{self.df3min['open_time'].iloc[i - 1]}, last_close_price:{self.df3min['close'].iloc[i - 1]}, i:{i}, 信号:'空'")
                break
            elif (  # 背离信号
                    (self.df3min['close'].iloc[current_macdhist] < self.df3min['close'].iloc[i - 1]) and
                    # 背离信号
                    (self.df3min['rsi'].iloc[current_macdhist] > self.df3min['rsi'].iloc[i - 1]) and
                    # 确认偏离过于确认
                    (self.df3min['rsi'].iloc[i - 1] <= 30 and self.df3min['rsi'].iloc[current_macdhist] <= 30) and
                    # 避免入场机会过于偏离
                    self.df3min['close'].iloc[current_macdhist] < self.df3min['close'].iloc[current_macdhist + 1] < (
                            1 + 0.001) * self.df3min['close'].iloc[current_macdhist] and
                    # 确认趋势上身
                    self.df3min['macdhist'].iloc[current_macdhist] < self.df3min['macdhist'].iloc[
                        current_macdhist + 1] <= 0 and
                    # 极大值背离
                    (
                            self.df3min['close'].iloc[i] < self.df3min['close'].iloc[i - 1] and
                            self.df3min['close'].iloc[i] < self.df3min['close'].iloc[i - 2] and
                            self.df3min['close'].iloc[i] < self.df3min['close'].iloc[i - 3] and
                            self.df3min['close'].iloc[i] < self.df3min['close'].iloc[i + 1] and
                            self.df3min['close'].iloc[i] < self.df3min['close'].iloc[i + 2] and
                            self.df3min['close'].iloc[i] < self.df3min['close'].iloc[i + 3]
                    ) and
                    # 避免过于左侧。
                    countMacdhistBigThan >= 3 and
                    is_decreasing

            ):
                self.df3min['rsi_divergence_signal'].iloc[current_macdhist] = 1  # 1表示存在背离
                print(
                    f"3min, dateTime:{self.df3min['open_time'].iloc[current_macdhist]},close_price:{self.df3min['close'].iloc[current_macdhist]}, dateTime:{self.df3min['open_time'].iloc[i - 1]}, last_close_price:{self.df3min['close'].iloc[i - 1]}, i:{i}, 信号:'多'")
                break
        # td
        td_current_index = len(self.df3min) - 1
        td_current_close = self.df3min['close'].iloc[td_current_index]
        td_pre_close = self.df3min['close'].iloc[td_current_index - 1]
        td_pre_count = self.df3min['td_sequential'].iloc[td_current_index - 1]
        td_current_count = self.df3min['td_sequential'].iloc[td_current_index - 1]
        if td_current_close < td_pre_close:
            if td_pre_count < 0:
                td_current_count = td_pre_count - 1
            else:
                td_current_count = -1
        else:
            if td_pre_count > 0:
                td_current_count = td_pre_count + 1
            else:
                td_current_count = 1
        self.df3min['td_sequential'].iloc[td_current_index] = td_current_count

        # trend
        if self.current_pos == 0:
            if self.df3min['rsi_divergence_signal'].iloc[current_macdhist] == 1:
                self.buy(bar.close_price, self.trade_money / bar.close_price)  # 做多
            elif self.df3min['rsi_divergence_signal'].iloc[current_macdhist] == -1:
                self.short(bar.close_price, self.trade_money / bar.close_price)  # 做空
        # # macd
        for i in range(current_macdhist - 2, max(current_macdhist - 60, 1), -1):
            if (
                    (self.df3min['close'].iloc[current_macdhist] > self.df3min['close'].iloc[i - 1]) and
                    (self.df3min['macdhist'].iloc[current_macdhist] < self.df3min['macdhist'].iloc[i - 1])
            ):
                self.df3min['macd_divergence_signal'].iloc[i] = -1  # 1表示存在背离
            elif (
                    (self.df3min['close'].iloc[i] < self.df3min['close'].iloc[i - 1]) and
                    (self.df3min['macdhist'].iloc[i] > self.df3min['macdhist'].iloc[i - 1])):
                self.df3min['macd_divergence_signal'].iloc[i] = 1  # 1表示存在背离

        # # td9
        # countdown = 0
        # td_begin = max(len(self.df3min) - 100, 0)
        # last_close = self.df3min['close'].iloc[td_begin]  # 初始化上一个收盘价
        # for i in range(td_begin, len(self.df3min)):
        #     if self.df3min['close'].iloc[i] < last_close:
        #         if countdown < 0:
        #             countdown -= 1
        #         else:
        #             countdown = -1
        #     else:
        #         if countdown > 0:
        #             countdown += 1
        #         else:
        #             countdown = 1
        #     self.df3min['td_sequential'].iloc[i] = countdown
        #     if countdown == 9 or countdown == -9:
        #         countdown = 0
        # if self.df3min['macdhist_directoin_count'][1] is not None:
        #     if self.df3min['macdhist_directoin_count'][1] > 0 and self.self.df3min['macdhist'][0] > 0:
        #         self.df3min['macdhist_directoin_count'][0] = self.df3min['macdhist_directoin_count'][1] + 1
        #     elif self.df3min['macdhist_directoin_count'][1] < 0 and self.self.df3min['macdhist'][0] < 0:
        #         self.df3min['macdhist_directoin_count'][0] = self.df3min['macdhist_directoin_count'][1] - 1
        #     elif self.self.df3min['macdhist'][0] > 0:
        #         self.df3min['macdhist_directoin_count'][0] = 1
        #     elif self.self.df3min['macdhist'][0] < 0:
        #         self.df3min['macdhist_directoin_count'][0] = -1
        # else:
        #     if self.self.df3min['macdhist'][0] > 0:
        #         self.df3min['macdhist_directoin_count'][0] = 1
        #     else:
        #         self.df3min['macdhist_directoin_count'][0] = -1
        #
        #
        # self.df3min['rsi'] = talib.RSI(self.df3min['close'])
        # self.df3min['macdhist_directoin_count'][1]
        # length = len(self.df3min['macdhist'])
        # if length >= 3:
        #     left_macdhist = self.df3min['macdhist'][0]
        #     middle_macdhist = self.df3min['macdhist'][1]
        #     right_macdhist = self.df3min['macdhist'][2]
        #     # 极大值， 看空
        #     if min(left_macdhist, middle_macdhist,
        #            right_macdhist) > 0 and middle_macdhist > left_macdhist and middle_macdhist > right_macdhist and  self.df3min['macdhist_directoin_count'][1] > 3:
        #         up_offset = self.df3min['macdhist_directoin_count'][1]
        #         # 找到柱状第一个负值
        #         down_first_index = up_offset + 1;
        #         # 负值范围
        #         down_offset = self.df3min['macdhist_directoin_count'][down_first_index]
        #         # 第二组up
        #         up_second_index_end = down_offset + down_first_index
        #         # 范围
        #         up_second_index_begin_offset = self.df3min['macdhist_directoin_count'][up_second_index_end]
        #         # 计算开始
        #         up_second_index_begin =  up_second_index_end + up_second_index_begin_offset -2
        #
        #         while(up_second_index_begin > up_second_index_end):
        #             left_macdhist = self.df3min['macdhist'][up_second_index_begin + 1]
        #             middle_macdhist = self.df3min['macdhist'][up_second_index_begin]
        #             right_macdhist = self.df3min['macdhist'][up_second_index_begin - 1]
        #             if min(left_macdhist, middle_macdhist,
        #                    right_macdhist) > 0 and middle_macdhist > left_macdhist and middle_macdhist > right_macdhist and self.df3min['macdhist_directoin_count'][up_second_index_begin] > 3:
        #                 if(self.df3min['close'][up_second_index_begin] < self.df3min['close'][middle_macdhist] and self.df3min['macdhist'][up_second_index_begin] > self.df3min['macdhist'][middle_macdhist]):
        #
        #                     print("=======牛=============")

        # 小于 %2 的 反向背离止盈离
        # 大于 %2 的 反向信号止盈一部分， td9跟踪

        # 预进场, 不满足前置条件

        # 进场晚， 满足前置条件， 但是入场价格走远。

        # 半亩夏 + rsi < 30

        # rsi + 量能柱子趋势确认

        # 半木夏 三连

        # rsi 三连

        # rsi 高1 高2 低1， 高1 < 高2， 低1 < 高2， 低1> 高2

        # rsi 头肩底， 头肩膀

        # 如果价格在同一个震荡区域，就认为可以作为判断

        # 止盈
        # 抓针止盈
        # td9
        #

    def on_5min_bar(self, bar: BarData):
        new_row = {"open_time": bar.datetime,
                   'open': bar.open_price,
                   'high': bar.high_price,
                   'low': bar.low_price,
                   'close': bar.close_price,
                   'volume': bar.volume,
                   }
        self.df5min = self.df5min.append(new_row, ignore_index=True)
        self.df5min['macd'], self.df5min['macdsignal'], self.df5min['macdhist'] = talib.MACD(self.df5min['close'],
                                                                                             self.fast_ema_window,
                                                                                             self.slow_ema_window, 9)

        # rsi
        self.df5min['rsi'] = talib.RSI(self.df5min['close'], timeperiod=14)
        current_macdhist = len(self.df5min) - 2
        countMacdhistBigThan = 0
        countMacdhistLessThan = 0

        min_value = float('inf')
        max_value = float('-inf')

        # 检查 MACD 能量柱子是否三次递增或递减
        is_increasing = self.df5min['macdhist'].gt(0).tail(3).all()
        is_decreasing = self.df5min['macdhist'].lt(0).tail(3).all()

        for i in range(current_macdhist - 2, max(current_macdhist - 60, 1), -1):
            # 短暂过滤震荡
            if self.df5min['macdhist'].iloc[i] > 0:
                countMacdhistBigThan = countMacdhistBigThan + 1
            else:
                countMacdhistLessThan = countMacdhistLessThan - 1

            # min max
            min_value = min(min_value, self.df5min['close'].iloc[i - 1])
            max_value = max(max_value, self.df5min['close'].iloc[i - 1])

            if (
                    # 背离查找之前是最低点，如果经历一次最低点
                    max_value < self.df5min['close'].iloc[current_macdhist] and
                    # 背离信号
                    (self.df5min['close'].iloc[current_macdhist] > self.df5min['close'].iloc[i - 1]) and
                    # 背离信号
                    (self.df5min['rsi'].iloc[current_macdhist] < self.df5min['rsi'].iloc[i - 1]) and
                    # 确认偏离过于确认
                    (self.df5min['rsi'].iloc[i - 1] >= 70 and self.df5min['rsi'].iloc[current_macdhist] >= 70) and
                    # 避免入场机会过于偏离
                    self.df5min['close'].iloc[current_macdhist] > self.df5min['close'].iloc[current_macdhist + 1] > (
                    1 - 0.001) * self.df5min['close'].iloc[current_macdhist] and
                    # 确认下降趋势
                    self.df5min['macdhist'].iloc[current_macdhist] > self.df5min['macdhist'].iloc[
                current_macdhist + 1] >= 0 and
                    # 极大值背离
                    (
                            self.df5min['close'].iloc[i] > self.df5min['close'].iloc[i - 1] and
                            self.df5min['close'].iloc[i] > self.df5min['close'].iloc[i - 2] and
                            self.df5min['close'].iloc[i] > self.df5min['close'].iloc[i + 1] and
                            self.df5min['close'].iloc[i] > self.df5min['close'].iloc[i + 2]
                    ) and
                    # 避免过于左侧。
                    countMacdhistLessThan <= -3 and
                    is_increasing
            ):
                self.df5min['rsi_divergence_signal'].iloc[current_macdhist] = '空'  # 1表示存在背离
                print(
                    f"5min, dateTime:{self.df5min['open_time'].iloc[current_macdhist]},close_price:{self.df5min['close'].iloc[current_macdhist]}, dateTime:{self.df5min['open_time'].iloc[i - 1]}, last_close_price:{self.df5min['close'].iloc[i - 1]}, i:{i}, 信号:'空'")
                break
            elif (
                    min_value > self.df5min['close'].iloc[current_macdhist] and
                    # 背离信号
                    (self.df5min['close'].iloc[current_macdhist] < self.df5min['close'].iloc[i - 1]) and
                    # 背离信号
                    (self.df5min['rsi'].iloc[current_macdhist] > self.df5min['rsi'].iloc[i - 1]) and
                    # 确认偏离过于确认
                    (self.df5min['rsi'].iloc[i - 1] <= 30 and self.df5min['rsi'].iloc[current_macdhist] <= 30) and
                    # 避免入场机会过于偏离
                    self.df5min['close'].iloc[current_macdhist] < self.df5min['close'].iloc[current_macdhist + 1] < (
                            1 + 0.001) * self.df5min['close'].iloc[current_macdhist] and
                    # 确认趋势上身
                    self.df5min['macdhist'].iloc[current_macdhist] < self.df5min['macdhist'].iloc[
                        current_macdhist + 1] <= 0 and
                    # 极大值背离
                    (
                            self.df5min['close'].iloc[i] < self.df5min['close'].iloc[i - 1] and
                            self.df5min['close'].iloc[i] < self.df5min['close'].iloc[i - 2] and
                            self.df5min['close'].iloc[i] < self.df5min['close'].iloc[i - 3] and
                            self.df5min['close'].iloc[i] < self.df5min['close'].iloc[i + 1] and
                            self.df5min['close'].iloc[i] < self.df5min['close'].iloc[i + 2] and
                            self.df5min['close'].iloc[i] < self.df5min['close'].iloc[i + 3]
                    ) and
                    # 避免过于左侧。
                    countMacdhistBigThan >= 3
                    and is_decreasing

            ):
                self.df5min['rsi_divergence_signal'].iloc[current_macdhist] = '多'  # 1表示存在背离
                print(
                    f"5min, dateTime:{self.df5min['open_time'].iloc[current_macdhist]},close_price:{self.df5min['close'].iloc[current_macdhist]}, dateTime:{self.df5min['open_time'].iloc[i - 1]}, last_close_price:{self.df5min['close'].iloc[i - 1]}, i:{i}, 信号:'多'")
                break

    def on_15min_bar(self, bar: BarData):
        new_row = {"open_time": bar.datetime,
                   'open': bar.open_price,
                   'high': bar.high_price,
                   'low': bar.low_price,
                   'close': bar.close_price,
                   'volume': bar.volume,
                   }
        self.df15min = self.df15min.append(new_row, ignore_index=True)
        self.df15min['macd'], self.df15min['macdsignal'], self.df15min['macdhist'] = talib.MACD(self.df15min['close'],
                                                                                                self.fast_ema_window,
                                                                                                self.slow_ema_window, 9)

        # rsi
        self.df15min['rsi'] = talib.RSI(self.df15min['close'], timeperiod=14)
        current_macdhist = len(self.df15min) - 2
        countMacdhistBigThan = 0
        countMacdhistLessThan = 0

        min_value = float('inf')
        max_value = float('-inf')

        # 检查 MACD 能量柱子是否三次递增或递减
        is_increasing = self.df15min['macdhist'].gt(0).tail(3).all()
        is_decreasing = self.df15min['macdhist'].lt(0).tail(3).all()

        for i in range(current_macdhist - 2, max(current_macdhist - 60, 1), -1):
            # 短暂过滤震荡
            if self.df15min['macdhist'].iloc[i] > 0:
                countMacdhistBigThan = countMacdhistBigThan + 1
            else:
                countMacdhistLessThan = countMacdhistLessThan - 1

            # min max
            min_value = min(min_value, self.df15min['close'].iloc[i - 1])
            max_value = max(max_value, self.df15min['close'].iloc[i - 1])

            if (
                    # 背离查找之前是最低点，如果经历一次最低点
                    max_value < self.df15min['close'].iloc[current_macdhist] and
                    # 背离信号
                    (self.df15min['close'].iloc[current_macdhist] > self.df15min['close'].iloc[i - 1]) and
                    # 背离信号
                    (self.df15min['rsi'].iloc[current_macdhist] < self.df15min['rsi'].iloc[i - 1]) and
                    # 确认偏离过于确认
                    (self.df15min['rsi'].iloc[i - 1] >= 70) and
                    # 避免入场机会过于偏离
                    self.df15min['close'].iloc[current_macdhist] > self.df15min['close'].iloc[current_macdhist + 1] > (
                    1 - 0.01) * self.df15min['close'].iloc[current_macdhist] and
                    # 确认下降趋势
                    self.df15min['macdhist'].iloc[current_macdhist] > self.df15min['macdhist'].iloc[
                current_macdhist + 1] >= 0 and
                    # 极大值背离
                    (
                            self.df15min['close'].iloc[i] > self.df15min['close'].iloc[i - 1] and
                            self.df15min['close'].iloc[i] > self.df15min['close'].iloc[i - 2] and
                            self.df15min['close'].iloc[i] > self.df15min['close'].iloc[i - 3] and
                            self.df15min['close'].iloc[i] > self.df15min['close'].iloc[i + 1] and
                            self.df15min['close'].iloc[i] > self.df15min['close'].iloc[i + 2] and
                            self.df15min['close'].iloc[i] > self.df15min['close'].iloc[i + 3]
                    ) and
                    # 避免过于左侧。
                    countMacdhistLessThan <= -3 and
                    is_increasing

            ):
                self.df15min['rsi_divergence_signal'].iloc[current_macdhist] = '空'  # 1表示存在背离
                print(
                    f"15min, dateTime:{self.df15min['open_time'].iloc[current_macdhist]},close_price:{self.df15min['close'].iloc[current_macdhist]}, dateTime:{self.df15min['open_time'].iloc[i - 1]}, last_close_price:{self.df15min['close'].iloc[i - 1]}, i:{i}, 信号:'空'")
                break
            elif (
                    min_value > self.df15min['close'].iloc[current_macdhist] and
                    # 背离信号
                    (self.df15min['close'].iloc[current_macdhist] < self.df15min['close'].iloc[i - 1]) and
                    # 背离信号
                    (self.df15min['rsi'].iloc[current_macdhist] > self.df15min['rsi'].iloc[i - 1]) and
                    # 确认偏离过于确认
                    (self.df15min['rsi'].iloc[i - 1] <= 30) and
                    # 避免入场机会过于偏离
                    self.df15min['close'].iloc[current_macdhist] < self.df15min['close'].iloc[current_macdhist + 1] < (
                            1 + 0.01) * self.df15min['close'].iloc[current_macdhist] and
                    # 确认趋势上身
                    self.df15min['macdhist'].iloc[current_macdhist] < self.df15min['macdhist'].iloc[
                        current_macdhist + 1] <= 0 and
                    # 极大值背离
                    (
                            self.df15min['close'].iloc[i] < self.df15min['close'].iloc[i - 1] and
                            self.df15min['close'].iloc[i] < self.df15min['close'].iloc[i - 2] and
                            self.df15min['close'].iloc[i] < self.df15min['close'].iloc[i - 3] and
                            self.df15min['close'].iloc[i] < self.df15min['close'].iloc[i + 1] and
                            self.df15min['close'].iloc[i] < self.df15min['close'].iloc[i + 2] and
                            self.df15min['close'].iloc[i] < self.df15min['close'].iloc[i + 3]
                    ) and
                    # 避免过于左侧。
                    countMacdhistBigThan >= 3 and
                    is_decreasing

            ):
                self.df15min['rsi_divergence_signal'].iloc[current_macdhist] = '多'  # 1表示存在背离
                print(
                    f"15min, dateTime:{self.df15min['open_time'].iloc[current_macdhist]},close_price:{self.df15min['close'].iloc[current_macdhist]}, dateTime:{self.df15min['open_time'].iloc[i - 1]}, last_close_price:{self.df15min['close'].iloc[i - 1]}, i:{i}, 信号:'多'")
                break

    def on_30min_bar(self, bar: BarData):
        new_row = {"open_time": bar.datetime,
                   'open': bar.open_price,
                   'high': bar.high_price,
                   'low': bar.low_price,
                   'close': bar.close_price,
                   'volume': bar.volume,
                   }
        self.df30min = self.df30min.append(new_row, ignore_index=True)
        self.df30min['macd'], self.df30min['macdsignal'], self.df30min['macdhist'] = talib.MACD(self.df30min['close'],
                                                                                                self.fast_ema_window,
                                                                                                self.slow_ema_window, 9)

        # rsi
        self.df30min['rsi'] = talib.RSI(self.df30min['close'], timeperiod=14)
        current_macdhist = len(self.df30min) - 2
        countMacdhistBigThan = 0
        countMacdhistLessThan = 0

        min_value = float('inf')
        max_value = float('-inf')

        # 检查 MACD 能量柱子是否三次递增或递减
        is_increasing = self.df30min['macdhist'].gt(0).tail(3).all()
        is_decreasing = self.df30min['macdhist'].lt(0).tail(3).all()

        for i in range(current_macdhist - 2, max(current_macdhist - 60, 1), -1):
            # 短暂过滤震荡
            if self.df30min['macdhist'].iloc[i] > 0:
                countMacdhistBigThan = countMacdhistBigThan + 1
            else:
                countMacdhistLessThan = countMacdhistLessThan - 1

            # min max
            min_value = min(min_value, self.df30min['close'].iloc[i - 1])
            max_value = max(max_value, self.df30min['close'].iloc[i - 1])

            if (
                    # 背离查找之前是最低点，如果经历一次最低点
                    max_value < self.df30min['close'].iloc[current_macdhist] and
                    # 背离信号
                    (self.df30min['close'].iloc[current_macdhist] > self.df30min['close'].iloc[i - 1]) and
                    # 背离信号
                    (self.df30min['rsi'].iloc[current_macdhist] < self.df30min['rsi'].iloc[i - 1]) and
                    # 确认偏离过于确认
                    (self.df30min['rsi'].iloc[i - 1] >= 70) and
                    # 避免入场机会过于偏离
                    self.df30min['close'].iloc[current_macdhist] > self.df30min['close'].iloc[current_macdhist + 1] > (
                    1 - 0.01) * self.df30min['close'].iloc[current_macdhist] and
                    # 确认下降趋势
                    self.df30min['macdhist'].iloc[current_macdhist] > self.df30min['macdhist'].iloc[
                current_macdhist + 1] >= 0 and
                    # 极大值背离
                    (
                            self.df30min['close'].iloc[i] > self.df30min['close'].iloc[i - 1] and
                            self.df30min['close'].iloc[i] > self.df30min['close'].iloc[i - 2] and
                            self.df30min['close'].iloc[i] > self.df30min['close'].iloc[i - 3] and
                            self.df30min['close'].iloc[i] > self.df30min['close'].iloc[i + 1] and
                            self.df30min['close'].iloc[i] > self.df30min['close'].iloc[i + 2] and
                            self.df30min['close'].iloc[i] > self.df30min['close'].iloc[i + 3]
                    ) and
                    # 避免过于左侧。
                    countMacdhistLessThan <= -3 and
                    is_increasing

            ):
                self.df30min['rsi_divergence_signal'].iloc[current_macdhist] = '空'  # 1表示存在背离
                print(
                    f"15min, dateTime:{self.df30min['open_time'].iloc[current_macdhist]},close_price:{self.df30min['close'].iloc[current_macdhist]}, dateTime:{self.df30min['open_time'].iloc[i - 1]}, last_close_price:{self.df30min['close'].iloc[i - 1]}, i:{i}, 信号:'空'")
                break
            elif (
                    min_value > self.df30min['close'].iloc[current_macdhist] and
                    # 背离信号
                    (self.df30min['close'].iloc[current_macdhist] < self.df30min['close'].iloc[i - 1]) and
                    # 背离信号
                    (self.df30min['rsi'].iloc[current_macdhist] > self.df30min['rsi'].iloc[i - 1]) and
                    # 确认偏离过于确认
                    (self.df30min['rsi'].iloc[i - 1] <= 30) and
                    # 避免入场机会过于偏离
                    self.df30min['close'].iloc[current_macdhist] < self.df30min['close'].iloc[current_macdhist + 1] < (
                            1 + 0.01) * self.df30min['close'].iloc[current_macdhist] and
                    # 确认趋势上身
                    self.df30min['macdhist'].iloc[current_macdhist] < self.df30min['macdhist'].iloc[
                        current_macdhist + 1] <= 0 and
                    # 极大值背离
                    (
                            self.df30min['close'].iloc[i] < self.df15min['close'].iloc[i - 1] and
                            self.df30min['close'].iloc[i] < self.df15min['close'].iloc[i - 2] and
                            self.df30min['close'].iloc[i] < self.df15min['close'].iloc[i - 3] and
                            self.df30min['close'].iloc[i] < self.df30min['close'].iloc[i + 1] and
                            self.df30min['close'].iloc[i] < self.df30min['close'].iloc[i + 2] and
                            self.df30min['close'].iloc[i] < self.df30min['close'].iloc[i + 3]
                    ) and
                    # 避免过于左侧。
                    countMacdhistBigThan >= 3 and
                    is_decreasing

            ):
                self.df30min['rsi_divergence_signal'].iloc[current_macdhist] = '多'  # 1表示存在背离
                print(
                    f"15min, dateTime:{self.df30min['open_time'].iloc[current_macdhist]},close_price:{self.df30min['close'].iloc[current_macdhist]}, dateTime:{self.df30min['open_time'].iloc[i - 1]}, last_close_price:{self.df30min['close'].iloc[i - 1]}, i:{i}, 信号:'多'")
                break

    def on_1h_bar(self, bar: BarData):
        new_row = {"open_time": bar.datetime,
                   'open': bar.open_price,
                   'high': bar.high_price,
                   'low': bar.low_price,
                   'close': bar.close_price,
                   'volume': bar.volume,
                   }
        self.df1h = self.df1h.append(new_row, ignore_index=True)
        self.df1h['macd'], self.df1h['macdsignal'], self.df1h['macdhist'] = talib.MACD(self.df1h['close'],
                                                                                       self.fast_ema_window,
                                                                                       self.slow_ema_window, 9)

        # rsi
        self.df1h['rsi'] = talib.RSI(self.df1h['close'], timeperiod=14)
        current_macdhist = len(self.df1h) - 2
        countMacdhistBigThan = 0
        countMacdhistLessThan = 0

        min_value = float('inf')
        max_value = float('-inf')

        # 检查 MACD 能量柱子是否三次递增或递减
        is_increasing = self.df1h['macdhist'].gt(0).tail(3).all()
        is_decreasing = self.df1h['macdhist'].lt(0).tail(3).all()

        for i in range(current_macdhist - 2, max(current_macdhist - 60, 1), -1):
            # 短暂过滤震荡
            if self.df1h['macdhist'].iloc[i] > 0:
                countMacdhistBigThan = countMacdhistBigThan + 1
            else:
                countMacdhistLessThan = countMacdhistLessThan - 1

            # min max
            min_value = min(min_value, self.df1h['close'].iloc[i - 1])
            max_value = max(max_value, self.df1h['close'].iloc[i - 1])

            if (
                    # 背离查找之前是最低点，如果经历一次最低点
                    max_value < self.df1h['close'].iloc[current_macdhist] and
                    # 背离信号
                    (self.df1h['close'].iloc[current_macdhist] > self.df1h['close'].iloc[i - 1]) and
                    # 背离信号
                    (self.df1h['rsi'].iloc[current_macdhist] < self.df1h['rsi'].iloc[i - 1]) and
                    # 确认偏离过于确认
                    (self.df1h['rsi'].iloc[i - 1] >= 70) and
                    # 避免入场机会过于偏离
                    self.df1h['close'].iloc[current_macdhist] > self.df1h['close'].iloc[current_macdhist + 1] > (
                    1 - 0.01) * self.df1h['close'].iloc[current_macdhist] and
                    # 确认下降趋势
                    self.df1h['macdhist'].iloc[current_macdhist] > self.df1h['macdhist'].iloc[
                current_macdhist + 1] >= 0 and
                    # 极大值背离
                    (
                            self.df1h['close'].iloc[i] > self.df1h['close'].iloc[i - 1] and
                            self.df1h['close'].iloc[i] > self.df1h['close'].iloc[i - 2] and
                            self.df1h['close'].iloc[i] > self.df1h['close'].iloc[i - 3] and
                            self.df1h['close'].iloc[i] > self.df1h['close'].iloc[i + 1] and
                            self.df1h['close'].iloc[i] > self.df1h['close'].iloc[i + 2] and
                            self.df1h['close'].iloc[i] > self.df1h['close'].iloc[i + 3]
                    ) and
                    # 避免过于左侧。
                    countMacdhistLessThan <= -3 and
                    is_increasing

            ):
                self.df1h['rsi_divergence_signal'].iloc[current_macdhist] = '空'  # 1表示存在背离
                print(
                    f"1h, dateTime:{self.df1h['open_time'].iloc[current_macdhist]},close_price:{self.df1h['close'].iloc[current_macdhist]}, dateTime:{self.df1h['open_time'].iloc[i - 1]}, last_close_price:{self.df1h['close'].iloc[i - 1]}, i:{i}, 信号:'空'")
                break
            elif (
                    min_value > self.df1h['close'].iloc[current_macdhist] and
                    # 背离信号
                    (self.df1h['close'].iloc[current_macdhist] < self.df1h['close'].iloc[i - 1]) and
                    # 背离信号
                    (self.df1h['rsi'].iloc[current_macdhist] > self.df1h['rsi'].iloc[i - 1]) and
                    # 确认偏离过于确认
                    (self.df1h['rsi'].iloc[i - 1] <= 30) and
                    # 避免入场机会过于偏离
                    self.df1h['close'].iloc[current_macdhist] < self.df1h['close'].iloc[current_macdhist + 1] < (
                            1 + 0.01) * self.df1h['close'].iloc[current_macdhist] and
                    # 确认趋势上身
                    self.df1h['macdhist'].iloc[current_macdhist] < self.df1h['macdhist'].iloc[
                        current_macdhist + 1] <= 0 and
                    # 极大值背离
                    (
                            self.df1h['close'].iloc[i] < self.df1h['close'].iloc[i - 1] and
                            self.df1h['close'].iloc[i] < self.df1h['close'].iloc[i - 2] and
                            self.df1h['close'].iloc[i] < self.df1h['close'].iloc[i - 3] and
                            self.df1h['close'].iloc[i] < self.df1h['close'].iloc[i + 1] and
                            self.df1h['close'].iloc[i] < self.df1h['close'].iloc[i + 2] and
                            self.df1h['close'].iloc[i] < self.df1h['close'].iloc[i + 3]
                    ) and
                    # 避免过于左侧。
                    countMacdhistBigThan >= 3 and
                    is_decreasing

            ):
                self.df1h['rsi_divergence_signal'].iloc[current_macdhist] = '多'  # 1表示存在背离
                print(
                    f"1h, dateTime:{self.df1h['open_time'].iloc[current_macdhist]},close_price:{self.df1h['close'].iloc[current_macdhist]}, dateTime:{self.df1h['open_time'].iloc[i - 1]}, last_close_price:{self.df1h['close'].iloc[i - 1]}, i:{i}, 信号:'多'")
                break

    def on_2h_bar(self, bar: BarData):
        new_row = {"open_time": bar.datetime,
                   'open': bar.open_price,
                   'high': bar.high_price,
                   'low': bar.low_price,
                   'close': bar.close_price,
                   'volume': bar.volume,
                   }
        self.df2h = self.df2h.append(new_row, ignore_index=True)
        self.df2h['macd'], self.df2h['macdsignal'], self.df2h['macdhist'] = talib.MACD(self.df2h['close'],
                                                                                       self.fast_ema_window,
                                                                                       self.slow_ema_window, 9)

        # rsi
        self.df2h['rsi'] = talib.RSI(self.df2h['close'], timeperiod=14)
        current_macdhist = len(self.df2h) - 2
        countMacdhistBigThan = 0
        countMacdhistLessThan = 0

        min_value = float('inf')
        max_value = float('-inf')

        # 检查 MACD 能量柱子是否三次递增或递减
        is_increasing = self.df2h['macdhist'].gt(0).tail(3).all()
        is_decreasing = self.df2h['macdhist'].lt(0).tail(3).all()

        for i in range(current_macdhist - 2, max(current_macdhist - 60, 1), -1):
            # 短暂过滤震荡
            if self.df2h['macdhist'].iloc[i] > 0:
                countMacdhistBigThan = countMacdhistBigThan + 1
            else:
                countMacdhistLessThan = countMacdhistLessThan - 1

            # min max
            min_value = min(min_value, self.df2h['close'].iloc[i - 1])
            max_value = max(max_value, self.df2h['close'].iloc[i - 1])

            if (
                    # 背离查找之前是最低点，如果经历一次最低点
                    max_value < self.df2h['close'].iloc[current_macdhist] and
                    # 背离信号
                    (self.df2h['close'].iloc[current_macdhist] > self.df2h['close'].iloc[i - 1]) and
                    # 背离信号
                    (self.df2h['rsi'].iloc[current_macdhist] < self.df2h['rsi'].iloc[i - 1]) and
                    # 确认偏离过于确认
                    (self.df2h['rsi'].iloc[i - 1] >= 70) and
                    # 避免入场机会过于偏离
                    self.df2h['close'].iloc[current_macdhist] > self.df2h['close'].iloc[current_macdhist + 1] > (
                    1 - 0.01) * self.df2h['close'].iloc[current_macdhist] and
                    # 确认下降趋势
                    self.df2h['macdhist'].iloc[current_macdhist] > self.df2h['macdhist'].iloc[
                current_macdhist + 1] >= 0 and
                    # 极大值背离
                    (
                            self.df2h['close'].iloc[i] > self.df2h['close'].iloc[i - 1] and
                            self.df2h['close'].iloc[i] > self.df2h['close'].iloc[i - 2] and
                            self.df2h['close'].iloc[i] > self.df2h['close'].iloc[i - 3] and
                            self.df2h['close'].iloc[i] > self.df2h['close'].iloc[i + 1] and
                            self.df2h['close'].iloc[i] > self.df2h['close'].iloc[i + 2] and
                            self.df2h['close'].iloc[i] > self.df2h['close'].iloc[i + 3]
                    ) and
                    # 避免过于左侧。
                    countMacdhistLessThan <= -3 and
                    is_increasing

            ):
                self.df2h['rsi_divergence_signal'].iloc[current_macdhist] = '空'  # 1表示存在背离
                print(
                    f"2h, dateTime:{self.df2h['open_time'].iloc[current_macdhist]},close_price:{self.df2h['close'].iloc[current_macdhist]}, dateTime:{self.df2h['open_time'].iloc[i - 1]}, last_close_price:{self.df2h['close'].iloc[i - 1]}, i:{i}, 信号:'空'")
                break
            elif (
                    min_value > self.df2h['close'].iloc[current_macdhist] and
                    # 背离信号
                    (self.df2h['close'].iloc[current_macdhist] < self.df2h['close'].iloc[i - 1]) and
                    # 背离信号
                    (self.df2h['rsi'].iloc[current_macdhist] > self.df2h['rsi'].iloc[i - 1]) and
                    # 确认偏离过于确认
                    (self.df2h['rsi'].iloc[i - 1] <= 30) and
                    # 避免入场机会过于偏离
                    self.df2h['close'].iloc[current_macdhist] < self.df2h['close'].iloc[current_macdhist + 1] < (
                            1 + 0.01) * self.df2h['close'].iloc[current_macdhist] and
                    # 确认趋势上身
                    self.df2h['macdhist'].iloc[current_macdhist] < self.df2h['macdhist'].iloc[
                        current_macdhist + 1] <= 0 and
                    # 极大值背离
                    (
                            self.df2h['close'].iloc[i] < self.df2h['close'].iloc[i - 1] and
                            self.df2h['close'].iloc[i] < self.df2h['close'].iloc[i - 2] and
                            self.df2h['close'].iloc[i] < self.df2h['close'].iloc[i - 3] and
                            self.df2h['close'].iloc[i] < self.df2h['close'].iloc[i + 1] and
                            self.df2h['close'].iloc[i] < self.df2h['close'].iloc[i + 2] and
                            self.df2h['close'].iloc[i] < self.df2h['close'].iloc[i + 3]
                    ) and
                    # 避免过于左侧。
                    countMacdhistBigThan >= 3 and
                    is_decreasing

            ):
                self.df2h['rsi_divergence_signal'].iloc[current_macdhist] = '多'  # 1表示存在背离
                print(
                    f"2h, dateTime:{self.df2h['open_time'].iloc[current_macdhist]},close_price:{self.df2h['close'].iloc[current_macdhist]}, dateTime:{self.df2h['open_time'].iloc[i - 1]}, last_close_price:{self.df2h['close'].iloc[i - 1]}, i:{i}, 信号:'多'")
                break

    def on_3h_bar(self, bar: BarData):
        new_row = {"open_time": bar.datetime,
                   'open': bar.open_price,
                   'high': bar.high_price,
                   'low': bar.low_price,
                   'close': bar.close_price,
                   'volume': bar.volume,
                   }
        self.df3h = self.df3h.append(new_row, ignore_index=True)
        self.df3h['macd'], self.df3h['macdsignal'], self.df3h['macdhist'] = talib.MACD(self.df3h['close'],
                                                                                       self.fast_ema_window,
                                                                                       self.slow_ema_window,
                                                                                       9)

        # rsi
        self.df3h['rsi'] = talib.RSI(self.df3h['close'], timeperiod=14)
        current_macdhist = len(self.df3h) - 2
        countMacdhistBigThan = 0
        countMacdhistLessThan = 0

        min_value = float('inf')
        max_value = float('-inf')

        # 检查 MACD 能量柱子是否三次递增或递减
        is_increasing = self.df3h['macdhist'].gt(0).tail(3).all()
        is_decreasing = self.df3h['macdhist'].lt(0).tail(3).all()

        for i in range(current_macdhist - 2, max(current_macdhist - 60, 1), -1):
            # 短暂过滤震荡
            if self.df3h['macdhist'].iloc[i] > 0:
                countMacdhistBigThan = countMacdhistBigThan + 1
            else:
                countMacdhistLessThan = countMacdhistLessThan - 1

            # min max
            min_value = min(min_value, self.df3h['close'].iloc[i - 1])
            max_value = max(max_value, self.df3h['close'].iloc[i - 1])

            if (
                    # 背离查找之前是最低点，如果经历一次最低点
                    max_value < self.df3h['close'].iloc[current_macdhist] and
                    # 背离信号
                    (self.df3h['close'].iloc[current_macdhist] > self.df1h['close'].iloc[i - 1]) and
                    # 背离信号
                    (self.df1h['rsi'].iloc[current_macdhist] < self.df1h['rsi'].iloc[i - 1]) and
                    # 确认偏离过于确认
                    (self.df1h['rsi'].iloc[i - 1] >= 70) and
                    # 避免入场机会过于偏离
                    self.df1h['close'].iloc[current_macdhist] > self.df1h['close'].iloc[
                current_macdhist + 1] > (
                    1 - 0.01) * self.df1h['close'].iloc[current_macdhist] and
                    # 确认下降趋势
                    self.df1h['macdhist'].iloc[current_macdhist] > self.df1h['macdhist'].iloc[
                current_macdhist + 1] >= 0 and
                    # 极大值背离
                    (
                            self.df1h['close'].iloc[i] > self.df1h['close'].iloc[i - 1] and
                            self.df1h['close'].iloc[i] > self.df1h['close'].iloc[i - 2] and
                            self.df1h['close'].iloc[i] > self.df1h['close'].iloc[i - 3] and
                            self.df1h['close'].iloc[i] > self.df1h['close'].iloc[i + 1] and
                            self.df1h['close'].iloc[i] > self.df1h['close'].iloc[i + 2] and
                            self.df1h['close'].iloc[i] > self.df1h['close'].iloc[i + 3]
                    ) and
                    # 避免过于左侧。
                    countMacdhistLessThan <= -3 and
                    is_increasing

            ):
                self.df1h['rsi_divergence_signal'].iloc[current_macdhist] = '空'  # 1表示存在背离
                print(
                    f"3h, dateTime:{self.df1h['open_time'].iloc[current_macdhist]},close_price:{self.df1h['close'].iloc[current_macdhist]}, dateTime:{self.df1h['open_time'].iloc[i - 1]}, last_close_price:{self.df1h['close'].iloc[i - 1]}, i:{i}, 信号:'空'")
                break
            elif (
                    min_value > self.df1h['close'].iloc[current_macdhist] and
                    # 背离信号
                    (self.df1h['close'].iloc[current_macdhist] < self.df1h['close'].iloc[i - 1]) and
                    # 背离信号
                    (self.df1h['rsi'].iloc[current_macdhist] > self.df1h['rsi'].iloc[i - 1]) and
                    # 确认偏离过于确认
                    (self.df1h['rsi'].iloc[i - 1] <= 30) and
                    # 避免入场机会过于偏离
                    self.df1h['close'].iloc[current_macdhist] < self.df1h['close'].iloc[
                        current_macdhist + 1] < (
                            1 + 0.01) * self.df1h['close'].iloc[current_macdhist] and
                    # 确认趋势上身
                    self.df1h['macdhist'].iloc[current_macdhist] < self.df1h['macdhist'].iloc[
                        current_macdhist + 1] <= 0 and
                    # 极大值背离
                    (
                            self.df1h['close'].iloc[i] < self.df1h['close'].iloc[i - 1] and
                            self.df1h['close'].iloc[i] < self.df1h['close'].iloc[i - 2] and
                            self.df1h['close'].iloc[i] < self.df1h['close'].iloc[i - 3] and
                            self.df1h['close'].iloc[i] < self.df1h['close'].iloc[i + 1] and
                            self.df1h['close'].iloc[i] < self.df1h['close'].iloc[i + 2] and
                            self.df1h['close'].iloc[i] < self.df1h['close'].iloc[i + 3]
                    ) and
                    # 避免过于左侧。
                    countMacdhistBigThan >= 3 and
                    is_decreasing

            ):
                self.df1h['rsi_divergence_signal'].iloc[current_macdhist] = '多'  # 1表示存在背离
                print(
                    f"3h, dateTime:{self.df1h['open_time'].iloc[current_macdhist]},close_price:{self.df1h['close'].iloc[current_macdhist]}, dateTime:{self.df1h['open_time'].iloc[i - 1]}, last_close_price:{self.df1h['close'].iloc[i - 1]}, i:{i}, 信号:'多'")
                break

    def on_45min_bar(self, bar: BarData):
        new_row = {"open_time": bar.datetime,
                   'open': bar.open_price,
                   'high': bar.high_price,
                   'low': bar.low_price,
                   'close': bar.close_price,
                   'volume': bar.volume,
                   }
        self.df45min = self.df45min.append(new_row, ignore_index=True)
        self.df45min['macd'], self.df45min['macdsignal'], self.df45min['macdhist'] = talib.MACD(self.df45min['close'],
                                                                                                self.fast_ema_window,
                                                                                                self.slow_ema_window, 9)

        # rsi
        self.df45min['rsi'] = talib.RSI(self.df45min['close'], timeperiod=14)
        current_macdhist = len(self.df45min) - 2
        countMacdhistBigThan = 0
        countMacdhistLessThan = 0

        min_value = float('inf')
        max_value = float('-inf')

        # 检查 MACD 能量柱子是否三次递增或递减
        is_increasing = self.df45min['macdhist'].gt(0).tail(3).all()
        is_decreasing = self.df45min['macdhist'].lt(0).tail(3).all()

        for i in range(current_macdhist - 2, max(current_macdhist - 60, 1), -1):
            # 短暂过滤震荡
            if self.df45min['macdhist'].iloc[i] > 0:
                countMacdhistBigThan = countMacdhistBigThan + 1
            else:
                countMacdhistLessThan = countMacdhistLessThan - 1

            # min max
            min_value = min(min_value, self.df45min['close'].iloc[i - 1])
            max_value = max(max_value, self.df45min['close'].iloc[i - 1])

            if (
                    # 背离查找之前是最低点，如果经历一次最低点
                    max_value < self.df45min['close'].iloc[current_macdhist] and
                    # 背离信号
                    (self.df45min['close'].iloc[current_macdhist] > self.df45min['close'].iloc[i - 1]) and
                    # 背离信号
                    (self.df45min['rsi'].iloc[current_macdhist] < self.df45min['rsi'].iloc[i - 1]) and
                    # 确认偏离过于确认
                    (self.df45min['rsi'].iloc[i - 1] >= 70) and
                    # 避免入场机会过于偏离
                    self.df45min['close'].iloc[current_macdhist] > self.df45min['close'].iloc[current_macdhist + 1] > (
                    1 - 0.01) * self.df45min['close'].iloc[current_macdhist] and
                    # 确认下降趋势
                    self.df45min['macdhist'].iloc[current_macdhist] > self.df45min['macdhist'].iloc[
                current_macdhist + 1] >= 0 and
                    # 极大值背离
                    (
                            self.df45min['close'].iloc[i] > self.df45min['close'].iloc[i - 1] and
                            self.df45min['close'].iloc[i] > self.df45min['close'].iloc[i - 2] and
                            self.df45min['close'].iloc[i] > self.df45min['close'].iloc[i - 3] and
                            self.df45min['close'].iloc[i] > self.df45min['close'].iloc[i + 1] and
                            self.df45min['close'].iloc[i] > self.df45min['close'].iloc[i + 2] and
                            self.df45min['close'].iloc[i] > self.df45min['close'].iloc[i + 3]
                    ) and
                    # 避免过于左侧。
                    countMacdhistLessThan <= -3 and
                    is_increasing
            ):
                self.df45min['rsi_divergence_signal'].iloc[current_macdhist] = '空'  # 1表示存在背离
                print(
                    f"45min, dateTime:{self.df45min['open_time'].iloc[current_macdhist]},close_price:{self.df45min['close'].iloc[current_macdhist]}, dateTime:{self.df45min['open_time'].iloc[i - 1]}, last_close_price:{self.df45min['close'].iloc[i - 1]}, i:{i}, 信号:'空'")
                break
            elif (
                    min_value > self.df45min['close'].iloc[current_macdhist] and
                    # 背离信号
                    (self.df45min['close'].iloc[current_macdhist] < self.df45min['close'].iloc[i - 1]) and
                    # 背离信号
                    (self.df45min['rsi'].iloc[current_macdhist] > self.df45min['rsi'].iloc[i - 1]) and
                    # 确认偏离过于确认
                    (self.df45min['rsi'].iloc[i - 1] <= 30) and
                    # 避免入场机会过于偏离
                    self.df45min['close'].iloc[current_macdhist] < self.df45min['close'].iloc[current_macdhist + 1] < (
                            1 + 0.01) * self.df45min['close'].iloc[current_macdhist] and
                    # 确认趋势上身
                    self.df45min['macdhist'].iloc[current_macdhist] < self.df45min['macdhist'].iloc[
                        current_macdhist + 1] <= 0 and
                    # 极大值背离
                    (
                            self.df45min['close'].iloc[i] < self.df45min['close'].iloc[i - 1] and
                            self.df45min['close'].iloc[i] < self.df45min['close'].iloc[i - 2] and
                            self.df45min['close'].iloc[i] < self.df45min['close'].iloc[i - 3] and
                            self.df45min['close'].iloc[i] < self.df45min['close'].iloc[i + 1] and
                            self.df45min['close'].iloc[i] < self.df45min['close'].iloc[i + 2] and
                            self.df45min['close'].iloc[i] < self.df45min['close'].iloc[i + 3]
                    ) and
                    # 避免过于左侧。
                    countMacdhistBigThan >= 3 and
                    is_decreasing
            ):
                self.df45min['rsi_divergence_signal'].iloc[current_macdhist] = '多'  # 1表示存在背离
                print(
                    f"45min, dateTime:{self.df45min['open_time'].iloc[current_macdhist]},close_price:{self.df45min['close'].iloc[current_macdhist]}, dateTime:{self.df45min['open_time'].iloc[i - 1]}, last_close_price:{self.df45min['close'].iloc[i - 1]}, i:{i}, 信号:'多'")
                break

    def on_4h_bar(self, bar: BarData):
        new_row = {"open_time": bar.datetime,
                   'open': bar.open_price,
                   'high': bar.high_price,
                   'low': bar.low_price,
                   'close': bar.close_price,
                   'volume': bar.volume,
                   }
        self.df4h = self.df4h.append(new_row, ignore_index=True)
        self.df4h['macd'], self.df4h['macdsignal'], self.df4h['macdhist'] = talib.MACD(self.df4h['close'],
                                                                                       self.fast_ema_window,
                                                                                       self.slow_ema_window, 9)

        # rsi
        self.df4h['rsi'] = talib.RSI(self.df4h['close'], timeperiod=14)
        current_macdhist = len(self.df4h) - 2
        countMacdhistBigThan = 0
        countMacdhistLessThan = 0

        min_value = float('inf')
        max_value = float('-inf')

        for i in range(current_macdhist - 2, max(current_macdhist - 60, 1), -1):
            # 短暂过滤震荡
            if self.df4h['macdhist'].iloc[i] > 0:
                countMacdhistBigThan = countMacdhistBigThan + 1
            else:
                countMacdhistLessThan = countMacdhistLessThan - 1

            # min max
            min_value = min(min_value, self.df4h['close'].iloc[i - 1])
            max_value = max(max_value, self.df4h['close'].iloc[i - 1])

            if (
                    # 背离查找之前是最低点，如果经历一次最低点
                    max_value < self.df4h['close'].iloc[current_macdhist] and
                    # 背离信号
                    (self.df4h['close'].iloc[current_macdhist] > self.df4h['close'].iloc[i - 1]) and
                    # 背离信号
                    (self.df4h['rsi'].iloc[current_macdhist] < self.df4h['rsi'].iloc[i - 1]) and
                    # 确认偏离过于确认
                    (self.df4h['rsi'].iloc[i - 1] >= 70) and
                    # 避免入场机会过于偏离
                    self.df4h['close'].iloc[current_macdhist] > self.df4h['close'].iloc[current_macdhist + 1] > (
                    1 - 0.01) * self.df4h['close'].iloc[current_macdhist] and
                    # 确认下降趋势
                    self.df4h['macdhist'].iloc[current_macdhist] > self.df4h['macdhist'].iloc[
                current_macdhist + 1] >= 0 and
                    # 极大值背离
                    (
                            self.df4h['close'].iloc[i] > self.df4h['close'].iloc[i - 1] and
                            self.df4h['close'].iloc[i] > self.df4h['close'].iloc[i - 2] and
                            self.df4h['close'].iloc[i] > self.df4h['close'].iloc[i + 1] and
                            self.df4h['close'].iloc[i] > self.df4h['close'].iloc[i + 2]
                    ) and
                    # 避免过于左侧。
                    countMacdhistLessThan <= -3
            ):
                self.df4h['rsi_divergence_signal'].iloc[current_macdhist] = '空'  # 1表示存在背离
                print(
                    f"4h, dateTime:{self.df4h['open_time'].iloc[current_macdhist]},close_price:{self.df4h['close'].iloc[current_macdhist]}, dateTime:{self.df4h['open_time'].iloc[i - 1]}, last_close_price:{self.df4h['close'].iloc[i - 1]}, i:{i}, 信号:'空'")
                break
            elif (
                    min_value > self.df4h['close'].iloc[current_macdhist] and
                    # 背离信号
                    (self.df4h['close'].iloc[current_macdhist] < self.df4h['close'].iloc[i - 1]) and
                    # 背离信号
                    (self.df4h['rsi'].iloc[current_macdhist] > self.df4h['rsi'].iloc[i - 1]) and
                    # 确认偏离过于确认
                    (self.df4h['rsi'].iloc[i - 1] <= 30) and
                    # 避免入场机会过于偏离
                    self.df4h['close'].iloc[current_macdhist] < self.df4h['close'].iloc[current_macdhist + 1] < (
                            1 + 0.01) * self.df4h['close'].iloc[current_macdhist] and
                    # 确认趋势上身
                    self.df4h['macdhist'].iloc[current_macdhist] < self.df4h['macdhist'].iloc[
                        current_macdhist + 1] <= 0 and
                    # 极大值背离
                    (
                            self.df4h['close'].iloc[i] < self.df4h['close'].iloc[i - 1] and
                            self.df4h['close'].iloc[i] < self.df4h['close'].iloc[i - 2] and
                            self.df4h['close'].iloc[i] < self.df4h['close'].iloc[i + 1] and
                            self.df4h['close'].iloc[i] < self.df4h['close'].iloc[i + 2]
                    ) and
                    # 避免过于左侧。
                    countMacdhistBigThan >= 3

            ):
                self.df4h['rsi_divergence_signal'].iloc[current_macdhist] = '多'  # 1表示存在背离
                print(
                    f"4h, dateTime:{self.df4h['open_time'].iloc[current_macdhist]},close_price:{self.df4h['close'].iloc[current_macdhist]}, dateTime:{self.df4h['open_time'].iloc[i - 1]}, last_close_price:{self.df4h['close'].iloc[i - 1]}, i:{i}, 信号:'多'")
                break

    def on_8h_bar(self, bar: BarData):
        new_row = {"open_time": bar.datetime,
                   'open': bar.open_price,
                   'high': bar.high_price,
                   'low': bar.low_price,
                   'close': bar.close_price,
                   'volume': bar.volume,
                   }
        self.df8h = self.df8h.append(new_row, ignore_index=True)
        self.df8h['macd'], self.df8h['macdsignal'], self.df8h['macdhist'] = talib.MACD(self.df8h['close'],
                                                                                       self.fast_ema_window,
                                                                                       self.slow_ema_window, 9)

        # rsi
        self.df8h['rsi'] = talib.RSI(self.df8h['close'], timeperiod=14)
        current_macdhist = len(self.df8h) - 2
        countMacdhistBigThan = 0
        countMacdhistLessThan = 0

        min_value = float('inf')
        max_value = float('-inf')

        for i in range(current_macdhist - 2, max(current_macdhist - 60, 1), -1):
            # 短暂过滤震荡
            if self.df8h['macdhist'].iloc[i] > 0:
                countMacdhistBigThan = countMacdhistBigThan + 1
            else:
                countMacdhistLessThan = countMacdhistLessThan - 1

            # min max
            min_value = min(min_value, self.df8h['close'].iloc[i - 1])
            max_value = max(max_value, self.df8h['close'].iloc[i - 1])

            if (
                    # 背离查找之前是最低点，如果经历一次最低点
                    max_value < self.df8h['close'].iloc[current_macdhist] and
                    # 背离信号
                    (self.df8h['close'].iloc[current_macdhist] > self.df8h['close'].iloc[i - 1]) and
                    # 背离信号
                    (self.df8h['rsi'].iloc[current_macdhist] < self.df8h['rsi'].iloc[i - 1]) and
                    # 确认偏离过于确认
                    (self.df8h['rsi'].iloc[i - 1] >= 70) and
                    # 避免入场机会过于偏离
                    self.df8h['close'].iloc[current_macdhist] > self.df8h['close'].iloc[current_macdhist + 1] > (
                    1 - 0.01) * self.df8h['close'].iloc[current_macdhist] and
                    # 确认下降趋势
                    self.df8h['macdhist'].iloc[current_macdhist] > self.df8h['macdhist'].iloc[
                current_macdhist + 1] >= 0 and
                    # 极大值背离
                    (
                            self.df8h['close'].iloc[i] > self.df8h['close'].iloc[i - 1] and
                            self.df8h['close'].iloc[i] > self.df8h['close'].iloc[i - 2] and
                            self.df8h['close'].iloc[i] > self.df8h['close'].iloc[i + 1] and
                            self.df8h['close'].iloc[i] > self.df8h['close'].iloc[i + 2]
                    ) and
                    # 避免过于左侧。
                    countMacdhistLessThan <= -3
            ):
                self.df8h['rsi_divergence_signal'].iloc[current_macdhist] = '空'  # 1表示存在背离
                print(
                    f"8h, dateTime:{self.df8h['open_time'].iloc[current_macdhist]},close_price:{self.df8h['close'].iloc[current_macdhist]}, dateTime:{self.df8h['open_time'].iloc[i - 1]}, last_close_price:{self.df8h['close'].iloc[i - 1]}, i:{i}, 信号:'空'")
                break
            elif (
                    min_value > self.df8h['close'].iloc[current_macdhist] and
                    # 背离信号
                    (self.df8h['close'].iloc[current_macdhist] < self.df8h['close'].iloc[i - 1]) and
                    # 背离信号
                    (self.df8h['rsi'].iloc[current_macdhist] > self.df8h['rsi'].iloc[i - 1]) and
                    # 确认偏离过于确认
                    (self.df8h['rsi'].iloc[i - 1] <= 30) and
                    # 避免入场机会过于偏离
                    self.df8h['close'].iloc[current_macdhist] < self.df8h['close'].iloc[current_macdhist + 1] < (
                            1 + 0.01) * self.df8h['close'].iloc[current_macdhist] and
                    # 确认趋势上身
                    self.df8h['macdhist'].iloc[current_macdhist] < self.df8h['macdhist'].iloc[
                        current_macdhist + 1] <= 0 and
                    # 极大值背离
                    (
                            self.df8h['close'].iloc[i] < self.df8h['close'].iloc[i - 1] and
                            self.df8h['close'].iloc[i] < self.df8h['close'].iloc[i - 2] and
                            self.df8h['close'].iloc[i] < self.df8h['close'].iloc[i + 1] and
                            self.df8h['close'].iloc[i] < self.df8h['close'].iloc[i + 2]
                    ) and
                    # 避免过于左侧。
                    countMacdhistBigThan >= 3

            ):
                self.df8h['rsi_divergence_signal'].iloc[current_macdhist] = '多'  # 1表示存在背离
                print(
                    f"8h, dateTime:{self.df8h['open_time'].iloc[current_macdhist]},close_price:{self.df8h['close'].iloc[current_macdhist]}, dateTime:{self.df8h['open_time'].iloc[i - 1]}, last_close_price:{self.df8h['close'].iloc[i - 1]}, i:{i}, 信号:'多'")
                break
    def on_12h_bar(self, bar: BarData):
        new_row = {"open_time": bar.datetime,
                   'open': bar.open_price,
                   'high': bar.high_price,
                   'low': bar.low_price,
                   'close': bar.close_price,
                   'volume': bar.volume,
                   }
        self.df12h = self.df12h.append(new_row, ignore_index=True)
        self.df12h['macd'], self.df12h['macdsignal'], self.df12h['macdhist'] = talib.MACD(self.df12h['close'],
                                                                                       self.fast_ema_window,
                                                                                       self.slow_ema_window, 9)

        # rsi
        self.df12h['rsi'] = talib.RSI(self.df12h['close'], timeperiod=14)
        current_macdhist = len(self.df12h) - 2
        countMacdhistBigThan = 0
        countMacdhistLessThan = 0

        min_value = float('inf')
        max_value = float('-inf')

        for i in range(current_macdhist - 2, max(current_macdhist - 60, 1), -1):
            # 短暂过滤震荡
            if self.df12h['macdhist'].iloc[i] > 0:
                countMacdhistBigThan = countMacdhistBigThan + 1
            else:
                countMacdhistLessThan = countMacdhistLessThan - 1

            # min max
            min_value = min(min_value, self.df12h['close'].iloc[i - 1])
            max_value = max(max_value, self.df12h['close'].iloc[i - 1])

            if (
                    # 背离查找之前是最低点，如果经历一次最低点
                    max_value < self.df12h['close'].iloc[current_macdhist] and
                    # 背离信号
                    (self.df12h['close'].iloc[current_macdhist] > self.df12h['close'].iloc[i - 1]) and
                    # 背离信号
                    (self.df12h['rsi'].iloc[current_macdhist] < self.df12h['rsi'].iloc[i - 1]) and
                    # 确认偏离过于确认
                    (self.df12h['rsi'].iloc[i - 1] >= 70) and
                    # 避免入场机会过于偏离
                    self.df12h['close'].iloc[current_macdhist] > self.df12h['close'].iloc[current_macdhist + 1] > (
                    1 - 0.01) * self.df12h['close'].iloc[current_macdhist] and
                    # 确认下降趋势
                    self.df12h['macdhist'].iloc[current_macdhist] > self.df12h['macdhist'].iloc[
                current_macdhist + 1] >= 0 and
                    # 极大值背离
                    (
                            self.df12h['close'].iloc[i] > self.df12h['close'].iloc[i - 1] and
                            self.df12h['close'].iloc[i] > self.df12h['close'].iloc[i - 2] and
                            self.df12h['close'].iloc[i] > self.df12h['close'].iloc[i + 1] and
                            self.df12h['close'].iloc[i] > self.df12h['close'].iloc[i + 2]
                    ) and
                    # 避免过于左侧。
                    countMacdhistLessThan <= -3
            ):
                self.df12h['rsi_divergence_signal'].iloc[current_macdhist] = '空'  # 1表示存在背离
                print(
                    f"8h, dateTime:{self.df12h['open_time'].iloc[current_macdhist]},close_price:{self.df12h['close'].iloc[current_macdhist]}, dateTime:{self.df12h['open_time'].iloc[i - 1]}, last_close_price:{self.df12h['close'].iloc[i - 1]}, i:{i}, 信号:'空'")
                break
            elif (
                    min_value > self.df12h['close'].iloc[current_macdhist] and
                    # 背离信号
                    (self.df12h['close'].iloc[current_macdhist] < self.df12h['close'].iloc[i - 1]) and
                    # 背离信号
                    (self.df12h['rsi'].iloc[current_macdhist] > self.df12h['rsi'].iloc[i - 1]) and
                    # 确认偏离过于确认
                    (self.df12h['rsi'].iloc[i - 1] <= 30) and
                    # 避免入场机会过于偏离
                    self.df12h['close'].iloc[current_macdhist] < self.df12h['close'].iloc[current_macdhist + 1] < (
                            1 + 0.01) * self.df12h['close'].iloc[current_macdhist] and
                    # 确认趋势上身
                    self.df12h['macdhist'].iloc[current_macdhist] < self.df12h['macdhist'].iloc[
                        current_macdhist + 1] <= 0 and
                    # 极大值背离
                    (
                            self.df12h['close'].iloc[i] < self.df12h['close'].iloc[i - 1] and
                            self.df12h['close'].iloc[i] < self.df12h['close'].iloc[i - 2] and
                            self.df12h['close'].iloc[i] < self.df12h['close'].iloc[i + 1] and
                            self.df12h['close'].iloc[i] < self.df12h['close'].iloc[i + 2]
                    ) and
                    # 避免过于左侧。
                    countMacdhistBigThan >= 3

            ):
                self.df12h['rsi_divergence_signal'].iloc[current_macdhist] = '多'  # 1表示存在背离
                print(
                    f"8h, dateTime:{self.df12h['open_time'].iloc[current_macdhist]},close_price:{self.df12h['close'].iloc[current_macdhist]}, dateTime:{self.df12h['open_time'].iloc[i - 1]}, last_close_price:{self.df12h['close'].iloc[i - 1]}, i:{i}, 信号:'多'")
                break

    def on_1d_bar(self, bar: BarData):
        new_row = {"open_time": bar.datetime,
                   'open': bar.open_price,
                   'high': bar.high_price,
                   'low': bar.low_price,
                   'close': bar.close_price,
                   'volume': bar.volume,
                   }
        self.df1d = self.df1d.append(new_row, ignore_index=True)
        self.df1d['macd'], self.df1d['macdsignal'], self.df1d['macdhist'] = talib.MACD(self.df1d['close'],
                                                                                       self.fast_ema_window,
                                                                                       self.slow_ema_window, 9)

        # rsi
        self.df1d['rsi'] = talib.RSI(self.df1d['close'], timeperiod=14)
        current_macdhist = len(self.df1d) - 2
        countMacdhistBigThan = 0
        countMacdhistLessThan = 0

        min_value = float('inf')
        max_value = float('-inf')

        for i in range(current_macdhist - 2, max(current_macdhist - 60, 1), -1):
            # 短暂过滤震荡
            if self.df1d['macdhist'].iloc[i] > 0:
                countMacdhistBigThan = countMacdhistBigThan + 1
            else:
                countMacdhistLessThan = countMacdhistLessThan - 1

            # min max
            min_value = min(min_value, self.df1d['close'].iloc[i - 1])
            max_value = max(max_value, self.df1d['close'].iloc[i - 1])

            if (
                    # 背离查找之前是最低点，如果经历一次最低点
                    max_value < self.df1d['close'].iloc[current_macdhist] and
                    # 背离信号
                    (self.df1d['close'].iloc[current_macdhist] > self.df1d['close'].iloc[i - 1]) and
                    # 背离信号
                    (self.df1d['rsi'].iloc[current_macdhist] < self.df1d['rsi'].iloc[i - 1]) and
                    # 确认偏离过于确认
                    (self.df1d['rsi'].iloc[i - 1] >= 70) and
                    # 避免入场机会过于偏离
                    self.df1d['close'].iloc[current_macdhist] > self.df1d['close'].iloc[current_macdhist + 1] > (
                    1 - 0.01) * self.df8h['close'].iloc[current_macdhist] and
                    # 确认下降趋势
                    self.df1d['macdhist'].iloc[current_macdhist] > self.df1d['macdhist'].iloc[
                current_macdhist + 1] >= 0 and
                    # 极大值背离
                    (
                            self.df1d['close'].iloc[i] > self.df1d['close'].iloc[i - 1] and
                            self.df1d['close'].iloc[i] > self.df1d['close'].iloc[i - 2] and
                            self.df1d['close'].iloc[i] > self.df1d['close'].iloc[i + 1] and
                            self.df1d['close'].iloc[i] > self.df1d['close'].iloc[i + 2]
                    ) and
                    # 避免过于左侧。
                    countMacdhistLessThan <= -3
            ):
                self.df1d['rsi_divergence_signal'].iloc[current_macdhist] = '空'  # 1表示存在背离
                print(
                    f"dateTime:{self.df1d['open_time'].iloc[current_macdhist]},close_price:{self.df1d['close'].iloc[current_macdhist]}, dateTime:{self.df1d['open_time'].iloc[i - 1]}, last_close_price:{self.df1d['close'].iloc[i - 1]}, i:{i}, 信号:'空'")
                break
            elif (
                    min_value > self.df1d['close'].iloc[current_macdhist] and
                    # 背离信号
                    (self.df1d['close'].iloc[current_macdhist] < self.df1d['close'].iloc[i - 1]) and
                    # 背离信号
                    (self.df1d['rsi'].iloc[current_macdhist] > self.df1d['rsi'].iloc[i - 1]) and
                    # 确认偏离过于确认
                    (self.df1d['rsi'].iloc[i - 1] <= 30) and
                    # 避免入场机会过于偏离
                    self.df1d['close'].iloc[current_macdhist] < self.df1d['close'].iloc[current_macdhist + 1] < (
                            1 + 0.01) * self.df1d['close'].iloc[current_macdhist] and
                    # 确认趋势上身
                    self.df1d['macdhist'].iloc[current_macdhist] < self.df1d['macdhist'].iloc[
                        current_macdhist + 1] <= 0 and
                    # 极大值背离
                    (
                            self.df1d['close'].iloc[i] < self.df1d['close'].iloc[i - 1] and
                            self.df1d['close'].iloc[i] < self.df1d['close'].iloc[i - 2] and
                            self.df1d['close'].iloc[i] < self.df1d['close'].iloc[i + 1] and
                            self.df1d['close'].iloc[i] < self.df1d['close'].iloc[i + 2]
                    ) and
                    # 避免过于左侧。
                    countMacdhistBigThan >= 3

            ):
                self.df1d['rsi_divergence_signal'].iloc[current_macdhist] = '多'  # 1表示存在背离
                print(
                    f"dateTime:{self.df1d['open_time'].iloc[current_macdhist]},close_price:{self.df1d['close'].iloc[current_macdhist]}, dateTime:{self.df1d['open_time'].iloc[i - 1]}, last_close_price:{self.df1d['close'].iloc[i - 1]}, i:{i}, 信号:'多'")
                break

    def on_1w_bar(self, bar: BarData):
        new_row = {"open_time": bar.datetime,
                   'open': bar.open_price,
                   'high': bar.high_price,
                   'low': bar.low_price,
                   'close': bar.close_price,
                   'volume': bar.volume,
                   }
        self.df1w = self.df1w.append(new_row, ignore_index=True)
        self.df1w['macd'], self.df1w['macdsignal'], self.df1w['macdhist'] = talib.MACD(self.df1d['close'],
                                                                                       self.fast_ema_window,
                                                                                       self.slow_ema_window, 9)

        # rsi
        self.df1w['rsi'] = talib.RSI(self.df1w['close'], timeperiod=14)
        current_macdhist = len(self.df1w) - 2
        countMacdhistBigThan = 0
        countMacdhistLessThan = 0

        min_value = float('inf')
        max_value = float('-inf')

        for i in range(current_macdhist - 2, max(current_macdhist - 60, 1), -1):
            # 短暂过滤震荡
            if self.df1w['macdhist'].iloc[i] > 0:
                countMacdhistBigThan = countMacdhistBigThan + 1
            else:
                countMacdhistLessThan = countMacdhistLessThan - 1

            # min max
            min_value = min(min_value, self.df1w['close'].iloc[i - 1])
            max_value = max(max_value, self.df1w['close'].iloc[i - 1])

            if (
                    # 背离查找之前是最低点，如果经历一次最低点
                    max_value < self.df1w['close'].iloc[current_macdhist] and
                    # 背离信号
                    (self.df1w['close'].iloc[current_macdhist] > self.df1w['close'].iloc[i - 1]) and
                    # 背离信号
                    (self.df1w['rsi'].iloc[current_macdhist] < self.df1w['rsi'].iloc[i - 1]) and
                    # 确认偏离过于确认
                    (self.df1w['rsi'].iloc[i - 1] >= 70) and
                    # 避免入场机会过于偏离
                    self.df1w['close'].iloc[current_macdhist] > self.df1w['close'].iloc[current_macdhist + 1] > (
                    1 - 0.01) * self.df8h['close'].iloc[current_macdhist] and
                    # 确认下降趋势
                    self.df1w['macdhist'].iloc[current_macdhist] > self.df1w['macdhist'].iloc[
                current_macdhist + 1] >= 0 and
                    # 极大值背离
                    (
                            self.df1w['close'].iloc[i] > self.df1w['close'].iloc[i - 1] and
                            self.df1w['close'].iloc[i] > self.df1w['close'].iloc[i - 2] and
                            self.df1w['close'].iloc[i] > self.df1w['close'].iloc[i + 1] and
                            self.df1w['close'].iloc[i] > self.df1w['close'].iloc[i + 2]
                    ) and
                    # 避免过于左侧。
                    countMacdhistLessThan <= -3
            ):
                self.df1w['rsi_divergence_signal'].iloc[current_macdhist] = '空'  # 1表示存在背离
                print(
                    f"dateTime:{self.df1w['open_time'].iloc[current_macdhist]},close_price:{self.df1w['close'].iloc[current_macdhist]}, dateTime:{self.df1w['open_time'].iloc[i - 1]}, last_close_price:{self.df1w['close'].iloc[i - 1]}, i:{i}, 信号:'空'")
                break
            elif (
                    min_value > self.df1w['close'].iloc[current_macdhist] and
                    # 背离信号
                    (self.df1w['close'].iloc[current_macdhist] < self.df1w['close'].iloc[i - 1]) and
                    # 背离信号
                    (self.df1w['rsi'].iloc[current_macdhist] > self.df1w['rsi'].iloc[i - 1]) and
                    # 确认偏离过于确认
                    (self.df1w['rsi'].iloc[i - 1] <= 30) and
                    # 避免入场机会过于偏离
                    self.df1w['close'].iloc[current_macdhist] < self.df1w['close'].iloc[current_macdhist + 1] < (
                            1 + 0.01) * self.df1w['close'].iloc[current_macdhist] and
                    # 确认趋势上身
                    self.df1w['macdhist'].iloc[current_macdhist] < self.df1w['macdhist'].iloc[
                        current_macdhist + 1] <= 0 and
                    # 极大值背离
                    (
                            self.df1w['close'].iloc[i] < self.df1w['close'].iloc[i - 1] and
                            self.df1w['close'].iloc[i] < self.df1w['close'].iloc[i - 2] and
                            self.df1w['close'].iloc[i] < self.df1w['close'].iloc[i + 1] and
                            self.df1w['close'].iloc[i] < self.df1w['close'].iloc[i + 2]
                    ) and
                    # 避免过于左侧。
                    countMacdhistBigThan >= 3

            ):
                self.df1w['rsi_divergence_signal'].iloc[current_macdhist] = '多'  # 1表示存在背离
                print(
                    f"dateTime:{self.df1w['open_time'].iloc[current_macdhist]},close_price:{self.df1w['close'].iloc[current_macdhist]}, dateTime:{self.df1w['open_time'].iloc[i - 1]}, last_close_price:{self.df1w['close'].iloc[i - 1]}, i:{i}, 信号:'多'")
                break


if __name__ == '__main__':
    engine = BacktestingEngine()

    engine.set_parameters(
        vt_symbol="BTCUSDT.BINANCE",
        # 分钟级别
        interval=Interval.MINUTE,
        start=datetime(2023, 1, 1),
        # 费率
        rate=7.5 / 10000,
        # 滑点
        slippage=0.5,

        size=1,

        # 价差
        pricetick=0.5,

        # 初始参数
        capital=100,

        end=datetime(2024, 3, 30)
    )

    engine.add_strategy(BitquantEmaStrategy, {})
    engine.load_data()
    engine.run_backtesting()
    engine.calculate_result()
    engine.calculate_statistics()
    engine.show_chart()
