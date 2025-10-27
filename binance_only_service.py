"""
币安独立监听服务 - 精简版
只监听Redis信号并在币安执行BTC期货交易
"""

import redis
import time
from simple_config import get_redis_config
from simple_signal_parser import SimpleSignalParser
from simple_binance_trader import SimpleBinanceTrader


class BinanceOnlyService:
    """币安独立交易服务"""
    
    def __init__(self):
        """初始化币安交易服务"""
        print("初始化币安交易服务...")
        
        # 初始化Redis
        self.redis_config = get_redis_config()
        self.redis_client = redis.Redis(
            host=self.redis_config.host,
            port=self.redis_config.port,
            password=self.redis_config.password,
            db=self.redis_config.db,
            decode_responses=self.redis_config.decode_responses
        )
        
        # 测试Redis连接
        try:
            self.redis_client.ping()
            print(f"Redis连接成功: {self.redis_config.host}:{self.redis_config.port}")
        except Exception as e:
            print(f"Redis连接失败: {e}")
            raise
        
        # 初始化组件
        self.signal_parser = SimpleSignalParser()
        
        try:
            self.binance_trader = SimpleBinanceTrader()
            print("币安交易客户端初始化成功")
        except Exception as e:
            print(f"币安交易客户端初始化失败: {e}")
            raise
        
        print("币安交易服务初始化完成")
    
    def handle_btc_signal(self, message: str):
        """处理BTC交易信号"""
        try:
            print(f"\n[币安] 收到信号: {message}")
            
            # 解析信号
            signal = self.signal_parser.parse_btc_signal(message)
            
            if not signal:
                print("[币安] 信号解析失败")
                return
            
            # 验证信号
            if not self.signal_parser.is_valid_btc_signal(signal):
                print("[币安] 信号验证失败")
                return
            
            # 执行交易
            self._execute_trade(signal)
            
        except Exception as e:
            print(f"[币安] 处理信号错误: {e}")
    
    def _execute_trade(self, signal):
        """执行交易"""
        print(f"[币安] 执行交易: {signal}")
        
        try:
            # 根据信号类型执行相应交易
            if signal.action == 'open_long':
                result = self.binance_trader.open_long(signal.quantity)
            elif signal.action == 'open_short':
                result = self.binance_trader.open_short(signal.quantity)
            elif signal.action == 'close_long':
                result = self.binance_trader.close_long(signal.quantity)
            elif signal.action == 'close_short':
                result = self.binance_trader.close_short(signal.quantity)
            else:
                print(f"[币安] 未知操作: {signal.action}")
                return
            
            # 检查结果
            if result.get('error'):
                print(f"[币安] 交易失败: {result['error']}")
            else:
                print(f"[币安] 交易成功: 订单ID {result.get('id')}")
                
        except Exception as e:
            print(f"[币安] 交易执行失败: {e}")
    
    def start_listening(self):
        """开始监听Redis频道（PUB/SUB模式）"""
        print(f"[币安] 开始订阅频道: {self.redis_config.trading_queue}")
        print("[币安] 按 Ctrl+C 停止服务\n")
        
        # 创建pubsub对象
        pubsub = self.redis_client.pubsub()
        
        try:
            # 订阅频道
            pubsub.subscribe(self.redis_config.trading_queue)
            print(f"[币安] 已订阅频道: {self.redis_config.trading_queue}")
            
            # 监听消息
            for message in pubsub.listen():
                try:
                    # 跳过订阅确认消息
                    if message['type'] == 'subscribe':
                        print(f"[币安] 订阅成功: {message['channel']}")
                        continue
                    
                    # 处理实际消息
                    if message['type'] == 'message':
                        data = message['data']
                        self.handle_btc_signal(data)
                    
                except redis.ConnectionError as e:
                    print(f"[币安] Redis连接错误: {e}")
                    time.sleep(5)
                    # 重新订阅
                    pubsub.subscribe(self.redis_config.trading_queue)
                except Exception as e:
                    print(f"[币安] 消息处理错误: {e}")
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            print("\n[币安] 停止服务")
        finally:
            pubsub.unsubscribe()
            pubsub.close()
            self.redis_client.close()


def main():
    """主函数"""
    try:
        service = BinanceOnlyService()
        service.start_listening()
    except Exception as e:
        print(f"[币安] 服务启动失败: {e}")


if __name__ == "__main__":
    main()
