"""
简化的币安期货交易类
只支持BTC市价单交易
"""

import ccxt
from simple_config import get_binance_config, BTC_SYMBOL


class SimpleBinanceTrader:
    def __init__(self):
        """初始化币安期货交易客户端"""
        config = get_binance_config()
        
        self.exchange = ccxt.binance({
            'apiKey': config.api_key,
            'secret': config.secret_key,
            'sandbox': False,  # 正式环境
            'options': {
                'defaultType': 'future',  # 期货交易
            },
        })
        
        self.leverage = config.leverage
        self._setup_leverage()
    
    def _setup_leverage(self):
        """设置BTC杠杆倍数和持仓模式"""
        try:
            # 设置为双向持仓模式
            # self.exchange.set_position_mode(hedged=True)
            # print(f"币安设置为双向持仓模式")
            
            # 设置杠杆
            result = self.exchange.set_leverage(self.leverage, BTC_SYMBOL)
            print(f"币安设置BTC杠杆 {self.leverage}x 成功")
        except Exception as e:
            print(f"币安设置失败: {e}")
    
    def open_long(self, quantity: float) -> dict:
        """开多仓"""
        return self._place_order('buy', quantity, position_side='LONG')
    
    def open_short(self, quantity: float) -> dict:
        """开空仓"""
        return self._place_order('sell', quantity, position_side='SHORT')
    
    def close_long(self, quantity: float) -> dict:
        """平多仓"""
        return self._place_order('sell', quantity, position_side='LONG')
    
    def close_short(self, quantity: float) -> dict:
        """平空仓"""
        return self._place_order('buy', quantity, position_side='SHORT')
    
    def _place_order(self, side: str, quantity: float, position_side: str = None) -> dict:
        """下市价单"""
        try:
            order_data = {
                'symbol': BTC_SYMBOL,
                'type': 'market',
                'side': side,
                'amount': quantity,
            }
            
            # 双向持仓模式需要指定持仓方向
            if position_side:
                order_data['params'] = {'positionSide': position_side}
            
            print(f"币安下单: {side} {quantity} BTC, 方向: {position_side}")
            
            order = self.exchange.create_order(**order_data)
            print(f"币安下单成功: {order.get('id')}")
            
            return order
            
        except Exception as e:
            error_msg = f"币安下单失败: {e}"
            print(error_msg)
            return {"error": error_msg}
    
    def get_balance(self) -> dict:
        """获取账户余额"""
        try:
            balance = self.exchange.fetch_balance()
            return balance
        except Exception as e:
            print(f"获取币安余额失败: {e}")
            return {}
    
    def get_positions(self) -> list:
        """获取BTC持仓"""
        try:
            positions = self.exchange.fetch_positions([BTC_SYMBOL])
            active_positions = [pos for pos in positions if float(pos['contracts']) > 0]
            return active_positions
        except Exception as e:
            print(f"获取币安持仓失败: {e}")
            return []