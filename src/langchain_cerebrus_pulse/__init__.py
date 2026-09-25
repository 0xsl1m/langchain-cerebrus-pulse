"""LangChain tools for Cerebrus Pulse crypto intelligence API."""

from importlib.metadata import PackageNotFoundError, version as _dist_version

from langchain_cerebrus_pulse.tools import (
    CerebrusPulseTool,
    CerebrusSentimentTool,
    CerebrusFundingTool,
    CerebrusBundleTool,
    CerebrusListCoinsTool,
    CerebrusScreenerTool,
    CerebrusOITool,
    CerebrusSpreadTool,
    CerebrusCorrelationTool,
    CerebrusStressTool,
    CerebrusCexDexTool,
    CerebrusBasisTool,
    CerebrusDepegTool,
    CerebrusLiquidationsTool,
)

try:
    __version__ = _dist_version("langchain-cerebrus-pulse")  # pyproject.toml is the one source
except PackageNotFoundError:  # a source tree that was never installed
    __version__ = "unknown"
__all__ = [
    "CerebrusPulseTool",
    "CerebrusSentimentTool",
    "CerebrusFundingTool",
    "CerebrusBundleTool",
    "CerebrusListCoinsTool",
    "CerebrusScreenerTool",
    "CerebrusOITool",
    "CerebrusSpreadTool",
    "CerebrusCorrelationTool",
    "CerebrusStressTool",
    "CerebrusCexDexTool",
    "CerebrusBasisTool",
    "CerebrusDepegTool",
    "CerebrusLiquidationsTool",
]
