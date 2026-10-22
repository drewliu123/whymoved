"""Resolve user input like "btc", "NVDA" or "$tsla" into an asset descriptor."""

from __future__ import annotations

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
    "亚马逊": "AMZN", "META": "META", "脸书": "META", "台积电": "TSM", "阿里巴巴": "BABA",
}


@dataclass(frozen=True)
class Asset:
    symbol: str          # canonical ticker, e.g. NVDA or BTC
    kind: str            # "stock" or "crypto"
    name: str            # human name for news search; refined later from price metadata
    exchange_tz: str     # timezone used to display times and to define "a day"

    @property
    def coinbase_product(self) -> str:
        return f"{self.symbol}-USD"


def resolve(raw: str) -> Asset:
    s = raw.strip().lstrip("$").upper()
    s = ALIASES.get(s, ALIASES.get(raw.strip(), s))
    for suffix in ("-USD", "USDT", "-USDT", "USD"):
        base = s[: -len(suffix)] if s.endswith(suffix) else None
        if base and base in CRYPTO:
            s = base
            break
    if s in CRYPTO:
        return Asset(symbol=s, kind="crypto", name=CRYPTO[s], exchange_tz="UTC")
    return Asset(symbol=s, kind="stock", name=s, exchange_tz="America/New_York")
