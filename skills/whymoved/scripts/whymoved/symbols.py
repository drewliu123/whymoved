"""Resolve user input like "btc", "NVDA", "$tsla", "0700.HK" or "600519" into an asset descriptor."""

from __future__ import annotations

import re
from dataclasses import dataclass

# Common crypto tickers -> human name used for news search.
CRYPTO = {
    "BTC": "Bitcoin", "ETH": "Ethereum", "SOL": "Solana", "XRP": "XRP", "DOGE": "Dogecoin",
    "ADA": "Cardano", "AVAX": "Avalanche", "LINK": "Chainlink", "DOT": "Polkadot",
    "LTC": "Litecoin", "BCH": "Bitcoin Cash", "UNI": "Uniswap", "AAVE": "Aave",
    "SHIB": "Shiba Inu", "PEPE": "Pepe", "SUI": "Sui", "APT": "Aptos", "ARB": "Arbitrum",
    "OP": "Optimism", "NEAR": "NEAR Protocol", "ATOM": "Cosmos", "HBAR": "Hedera",
    "XLM": "Stellar", "FIL": "Filecoin", "ICP": "Internet Computer", "TON": "Toncoin",
    "TRX": "TRON", "HYPE": "Hyperliquid", "ONDO": "Ondo", "ENA": "Ethena",
}

ALIASES = {
    "BITCOIN": "BTC", "ETHEREUM": "ETH", "SOLANA": "SOL", "DOGECOIN": "DOGE",
    "比特币": "BTC", "以太坊": "ETH", "以太币": "ETH", "狗狗币": "DOGE",
    "英伟达": "NVDA", "特斯拉": "TSLA", "苹果": "AAPL", "微软": "MSFT", "谷歌": "GOOGL",
    "亚马逊": "AMZN", "脸书": "META", "台积电": "TSM", "阿里巴巴": "BABA",
    "拼多多": "PDD", "京东": "JD", "百度": "BIDU", "蔚来": "NIO", "小鹏": "XPEV", "理想": "LI",
    # Hong Kong
    "腾讯": "0700.HK", "腾讯控股": "0700.HK", "美团": "3690.HK", "小米": "1810.HK", "小米集团": "1810.HK",
    "阿里巴巴港股": "9988.HK", "快手": "1024.HK", "比亚迪股份": "1211.HK", "港交所": "0388.HK",
    "汇丰": "0005.HK", "汇丰控股": "0005.HK", "友邦": "1299.HK", "中国移动": "0941.HK",
    "京东集团": "9618.HK", "网易": "9999.HK", "百度集团": "9888.HK", "泡泡玛特": "9992.HK",
    "中芯国际": "0981.HK", "理想汽车": "2015.HK", "蔚来港股": "9866.HK", "小鹏汽车": "9868.HK",
    "恒生指数": "^HSI",
    # Mainland A-shares
    "贵州茅台": "600519.SS", "茅台": "600519.SS", "宁德时代": "300750.SZ", "比亚迪": "002594.SZ",
    "招商银行": "600036.SS", "中国平安": "601318.SS", "五粮液": "000858.SZ", "工商银行": "601398.SS",
    "东方财富": "300059.SZ", "隆基绿能": "601012.SS", "中信证券": "600030.SS", "寒武纪": "688256.SS",
    "长江电力": "600900.SS", "美的集团": "000333.SZ", "海康威视": "002415.SZ", "立讯精密": "002475.SZ",
    "中际旭创": "300308.SZ", "工业富联": "601138.SS", "沪深300": "000300.SS", "上证指数": "000001.SS",
}

# Chinese names for news search in Chinese-language media (reverse of the aliases above).
ZH_NAME: dict[str, str] = {}
for _zh, _sym in ALIASES.items():
    if re.search(r"[一-鿿]", _zh) and not _zh.endswith("港股"):
        ZH_NAME.setdefault(_sym, _zh)

MARKETS = {
    # market: (timezone, regular session close as HH:MM local)
    "us": ("America/New_York", "16:00"),
    "hk": ("Asia/Hong_Kong", "16:00"),
    "cn": ("Asia/Shanghai", "15:00"),
    "crypto": ("UTC", ""),
}


@dataclass(frozen=True)
class Asset:
    symbol: str          # canonical ticker, e.g. NVDA, BTC, 0700.HK, 600519.SS
    kind: str            # "stock" or "crypto"
    name: str            # human name for news search; refined later from price metadata
    exchange_tz: str     # timezone used to display times and to define "a day"
    market: str = "us"   # "us", "hk", "cn" or "crypto"
    zh_name: str = ""    # Chinese name, used to search Chinese-language news

    @property
    def coinbase_product(self) -> str:
        return f"{self.symbol}-USD"

    @property
    def code(self) -> str:
        """Exchange code without the Yahoo suffix: 0700, 600519, NVDA."""
        return self.symbol.split(".")[0]


def _stock(symbol: str, market: str) -> Asset:
    tz = MARKETS[market][0]
    return Asset(symbol=symbol, kind="stock", name=symbol, exchange_tz=tz, market=market,
                 zh_name=ZH_NAME.get(symbol, ""))


def resolve(raw: str) -> Asset:
    s = raw.strip().lstrip("$").upper()
    s = ALIASES.get(s, ALIASES.get(raw.strip(), s))
    for suffix in ("-USD", "-USDT", "USDT", "USD"):
        base = s[: -len(suffix)] if s.endswith(suffix) else None
        if base and base in CRYPTO:
            s = base
            break
    if s in CRYPTO:
        return Asset(symbol=s, kind="crypto", name=CRYPTO[s], exchange_tz="UTC", market="crypto")

    # Hong Kong: 700, 0700, 00700, 0700.HK, HK0700
    m = re.fullmatch(r"(?:HK)?0*(\d{1,5})(?:\.HK)?", s)
    if m and (s.endswith(".HK") or s.startswith("HK") or len(s) <= 5):
        return _stock(f"{int(m.group(1)):04d}.HK", "hk")
    # Mainland: 600519, 600519.SS, 600519.SH, SH600519, 000001.SZ
    m = re.fullmatch(r"(SH|SZ)?(\d{6})(?:\.(SS|SH|SZ))?", s)
    if m:
        code, ex = m.group(2), (m.group(1) or m.group(3) or "")
        if ex in ("SS", "SH") or (not ex and code[0] in "569"):
            return _stock(f"{code}.SS", "cn")
        return _stock(f"{code}.SZ", "cn")
    if s == "^HSI":
        return _stock(s, "hk")
    return _stock(s.replace(".", "-"), "us")  # Yahoo spells BRK.B as BRK-B
