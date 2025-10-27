"""
简化的交易信号解析器
只处理BTC交易信号
"""

import re
from dataclasses import dataclass
from simple_config import SIGNAL_MAPPING, BTC_OKX_SYMBOL, convert_quantity


@dataclass
class BTCSignal:
    """BTC交易信号数据类"""
    action: str          # 操作类型: 'open_long', 'open_short', 'close_long', 'close_short'
    quantity: float      # 实际交易数量 (已转换)
    original_quantity: float  # 原始数量
    original_message: str     # 原始消息
    
    def __str__(self):
        return f"BTCSignal(action={self.action}, quantity={self.quantity})"


class SimpleSignalParser:
    """简化的信号解析器"""
    
    def __init__(self):
        # 只匹配BTC信号的正则表达式
        self.btc_pattern = re.compile(
            r'\[([^\]]+)\]\s*数量:([0-9.]+)\s*市场:BTC-USDT-SWAP',
            re.IGNORECASE
        )
    
    def parse_btc_signal(self, message: str) -> BTCSignal:
        """
        解析BTC交易信号
        
        Args:
            message: 原始消息字符串
            
        Returns:
            BTCSignal对象，解析失败返回None
        """
        try:
            message = message.strip()
            print(f"解析BTC信号: {message}")
            
            # 检查是否为BTC信号
            if BTC_OKX_SYMBOL not in message:
                print(f"非BTC信号，忽略: {message}")
                return None
            
            # 使用正则表达式匹配
            match = self.btc_pattern.search(message)
            
            if not match:
                print(f"BTC信号格式不匹配: {message}")
                return None
            
            # 提取操作和数量
            action_text = match.group(1).strip()
            quantity_text = match.group(2).strip()
            
            # 转换操作类型
            action = SIGNAL_MAPPING.get(action_text)
            if not action:
                print(f"未知的操作类型: {action_text}")
                return None
            
            # 转换数量
            try:
                original_quantity = float(quantity_text)
                actual_quantity = convert_quantity(original_quantity)
                
                if actual_quantity <= 0:
                    print(f"无效的交易数量: {actual_quantity}")
                    return None
                    
            except ValueError:
                print(f"无法解析数量: {quantity_text}")
                return None
            
            # 创建信号对象
            signal = BTCSignal(
                action=action,
                quantity=actual_quantity,
                original_quantity=original_quantity,
                original_message=message
            )
            
            print(f"BTC信号解析成功: {signal}")
            return signal
            
        except Exception as e:
            print(f"解析BTC信号时发生错误: {e}")
            return None
    
    def is_valid_btc_signal(self, signal: BTCSignal) -> bool:
        """验证BTC信号"""
        if not signal:
            return False
        
        # 检查操作类型
        valid_actions = ['open_long', 'open_short', 'close_long', 'close_short']
        if signal.action not in valid_actions:
            print(f"无效的操作类型: {signal.action}")
            return False
        
        # 检查数量
        if signal.quantity <= 0 or signal.quantity > 1:  # 限制最大数量为1 BTC
            print(f"无效的交易数量: {signal.quantity}")
            return False
        
        return True


def test_btc_parser():
    """测试BTC信号解析器"""
    parser = SimpleSignalParser()
    
    test_messages = [
        "[开多] 数量:1 市场:BTC-USDT-SWAP",
        "[开空] 数量:1 市场:BTC-USDT-SWAP",
        "[平多] 数量:1 市场:BTC-USDT-SWAP",
        "[平空] 数量:1 市场:BTC-USDT-SWAP",
        "[开多] 数量:2 市场:BTC-USDT-SWAP",
        "[开多] 数量:1 市场:ETH-USDT-SWAP",  # 非BTC信号
        "无效格式",
    ]
    
    print("=== BTC信号解析器测试 ===")
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n测试 {i}: {message}")
        
        signal = parser.parse_btc_signal(message)
        
        if signal:
            is_valid = parser.is_valid_btc_signal(signal)
            print(f"  解析结果: {signal}")
            print(f"  验证结果: {'通过' if is_valid else '失败'}")
            print(f"  原始数量: {signal.original_quantity} -> 实际数量: {signal.quantity}")
        else:
            print("  解析失败")


if __name__ == "__main__":
    test_btc_parser()