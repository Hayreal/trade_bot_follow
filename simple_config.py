"""
简化配置文件
只包含BTC交易的核心配置
"""

import os
import yaml
from dataclasses import dataclass
from typing import Optional, Dict
from pathlib import Path


@dataclass
class RedisConfig:
    """Redis配置类"""
    host: str = 'localhost'
    port: int = 6379
    password: Optional[str] = None
    db: int = 0
    decode_responses: bool = True
    trading_queue: str = 'okx:trading:signals'


@dataclass
class BinanceConfig:
    """币安API配置类"""
    api_key: str
    secret_key: str
    leverage: int = 150  # 100倍杠杆
    
    def __post_init__(self):
        if not self.api_key or not self.secret_key:
            raise ValueError("币安API密钥不能为空")

# 固定配置
BTC_SYMBOL = 'BTC/USDT'
BTC_OKX_SYMBOL = 'BTC-USDT-SWAP'

# 信号类型映射
SIGNAL_MAPPING = {
    '开多': 'open_long',
    '开空': 'open_short', 
    '平多': 'close_long',
    '平空': 'close_short'
}

# 全局配置缓存
_config_cache: Optional[Dict] = None


def _load_config() -> Dict:
    """加载YAML配置文件"""
    global _config_cache
    
    if _config_cache is not None:
        return _config_cache
    
    # 配置文件路径
    config_path = Path(__file__).parent / 'config.yaml'
    
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        _config_cache = yaml.safe_load(f)
    
    return _config_cache


def get_quantity_mapping() -> Dict[int, float]:
    """
    从配置文件获取数量映射
    
    Returns:
        数量映射字典
    """
    config = _load_config()
    return config.get('quantity_mapping', {1: 0.001})


def get_binance_config() -> BinanceConfig:
    """从配置文件获取币安配置"""
    config = _load_config()
    binance_config = config.get('binance', {})
    
    return BinanceConfig(
        api_key=binance_config.get('api_key', ''),
        secret_key=binance_config.get('secret_key', ''),
        leverage=binance_config.get('leverage', 150)
    )



def get_redis_config() -> RedisConfig:
    """从配置文件获取Redis配置"""
    config = _load_config()
    redis_config = config.get('redis', {})
    
    return RedisConfig(
        host=redis_config.get('host', 'localhost'),
        port=redis_config.get('port', 6379),
        password=redis_config.get('password'),
        db=redis_config.get('db', 0),
        decode_responses=redis_config.get('decode_responses', True),
        trading_queue=redis_config.get('trading_queue', 'okx:trading:signals')
    )


def convert_quantity(redis_quantity: float) -> float:
    """
    转换数量：Redis消息数量 -> 实际交易数量
    
    Args:
        redis_quantity: Redis消息中的数量
        
    Returns:
        实际交易数量
    """
    quantity_mapping = get_quantity_mapping()
    return quantity_mapping.get(int(redis_quantity), redis_quantity * 0.001)