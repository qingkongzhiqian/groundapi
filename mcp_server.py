"""
GroundAPI MCP Server — tools for AI Agents.

Finance: 4 tools covering all A-share data (69 BiyingAPI endpoints).
Info: 3 tools (search, scrape, news).
Life: 3 tools (weather, logistics, IP).

Requires Bearer-token authentication: the client must supply its own
GroundAPI API Key via ``Authorization: Bearer sk_gapi_...``.
"""

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
import httpx
from fastmcp import FastMCP
from fastmcp.server.auth.providers.debug import DebugTokenVerifier
from fastmcp.server.dependencies import get_access_token

_env_file = Path(__file__).resolve().parent.parent.parent / ".env"
if _env_file.exists():
    load_dotenv(_env_file)

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

auth = DebugTokenVerifier(
    validate=lambda token: token.startswith("sk_gapi_"),
)

mcp = FastMCP(
    "GroundAPI",
    auth=auth,
    instructions=(
        "One-stop data layer for AI Agents. "
        "Finance: A-share stock/index/ETF data (13 aspects), market overview (5 scopes), "
        "multi-dimensional screening, universal search across 11,780 securities. "
        "Info: web search, news, webpage scraping. "
        "Life: weather, logistics tracking, IP geolocation. "
        "Requires authentication: pass your GroundAPI API Key as a Bearer token."
    ),
)


async def _call(path: str, params: dict | None = None) -> dict:
    token: str = get_access_token()
    headers = {"Content-Type": "application/json", "X-API-Key": token}
    transport = httpx.AsyncHTTPTransport(proxy=None)
    async with httpx.AsyncClient(base_url=API_BASE, timeout=60, transport=transport) as client:
        resp = await client.get(path, params=params or {}, headers=headers)
        return resp.json()


# ---------------------------------------------------------------------------
# Finance (4 tools)
# ---------------------------------------------------------------------------

@mcp.tool()
async def finance_stock(
    symbol: str = "",
    keyword: str = "",
    aspects: str = "overview",
    days: int = 60,
    period: str = "d",
    limit: int = 10,
) -> dict:
    """Query any A-share security: individual stock, index, or ETF. Supports multi-stock comparison.

    MODES:
    - Single stock: finance_stock(symbol="000001") — default returns overview
    - Deep dive: finance_stock(symbol="000001", aspects="quote,technical,financial")
    - Index: finance_stock(symbol="000001.SH", aspects="kline,technical")
    - ETF: finance_stock(symbol="510300", aspects="quote")
    - Compare: finance_stock(symbol="000001,601398", aspects="quote")
    - Search: finance_stock(keyword="平安")

    ASPECTS (comma-separated):
    - overview: quick snapshot (quote + profile brief + financial brief)
    - profile: full company info, concepts, indices, capital structure
    - quote: realtime price, PE/PB, bid/ask 5-level, limit up/down distance
    - kline: K-line data (period: 5/15/30/60/d/w/m, front-adjusted)
    - technical: MACD/MA/BOLL/KDJ + market indicators + signal facts (e.g. "DIF上穿DEA")
    - financial: full financials — 3 statements, quarterly P&L, dividends, forecasts, industry comparison
    - flow: capital flow (4-tier: mega/large/medium/small orders), consecutive inflow/outflow days
    - holders: top10 shareholders, float holders, count trend, fund holdings
    - management: executives, board directors, supervisors
    - events: dividends, share issuance, lock-up expiry, earnings forecasts
    - tick: intraday tick data with buy/sell direction stats
    - summary: aggregated facts from quote+technical+financial+flow+holders (no opinions)
    - peers: same-industry comparison table with ranking"""
    if keyword:
        return await _call("/v1/finance/stock", {"keyword": keyword, "limit": limit})
    params: dict = {"aspects": aspects, "days": days, "period": period, "limit": limit}
    if symbol:
        params["symbol"] = symbol
    return await _call("/v1/finance/stock", params)


@mcp.tool()
async def finance_market(
    scope: str = "overview",
    sector: str = "",
    date: str = "",
    limit: int = 20,
) -> dict:
    """Get market-wide data: indices, hot stocks, sectors, IPO calendar, anomaly signals.

    SCOPES (comma-separated):
    - overview: major indices (SSE/SZSE/ChiNext/STAR50/BSE50) + sentiment (limit-up count, seal rate, max streak)
    - hot: limit-up/down/strong/failed-limit/sub-new stock pools with streak tier breakdown
    - sectors: concept & industry lists; add sector="AI" to drill into constituents
    - ipo: upcoming IPO calendar
    - signals: market-wide anomaly facts (multi-streak stocks, high-gain stocks)

    Examples:
    - "今天大盘" → finance_market()
    - "涨停股" → finance_market(scope="hot")
    - "AI概念成分股" → finance_market(scope="sectors", sector="AI")
    - "新股日历" → finance_market(scope="ipo")"""
    params: dict = {"scope": scope, "limit": limit}
    if sector:
        params["sector"] = sector
    if date:
        params["date"] = date
    return await _call("/v1/finance/market", params)


@mcp.tool()
async def finance_screen(
    industry: str = "",
    concept: str = "",
    pe_max: float = 0,
    pe_min: float = 0,
    pb_max: float = 0,
    min_market_cap: float = 0,
    max_market_cap: float = 0,
    min_dividend_yield: float = 0,
    filter_preset: str = "",
    sort_by: str = "change_pct",
    order: str = "desc",
    limit: int = 20,
) -> dict:
    """Screen stocks by valuation, size, yield, industry, or concept.

    All filters are optional. Omit all for a default ranking by change_pct.

    FILTER PRESETS (shortcut parameter combinations):
    - low_pe_high_div: PE<15 and dividend yield>3%
    - small_cap_growth: market cap<10B
    - large_cap_stable: market cap>50B and PE<20

    Examples:
    - "低估值银行股" → finance_screen(industry="银行", pe_max=10)
    - "高分红" → finance_screen(min_dividend_yield=3, sort_by="dividend_yield")
    - "AI概念" → finance_screen(concept="AI")"""
    params: dict = {"sort_by": sort_by, "order": order, "limit": limit}
    if industry:
        params["industry"] = industry
    if concept:
        params["concept"] = concept
    if pe_max > 0:
        params["pe_max"] = pe_max
    if pe_min > 0:
        params["pe_min"] = pe_min
    if pb_max > 0:
        params["pb_max"] = pb_max
    if min_market_cap > 0:
        params["min_market_cap"] = min_market_cap
    if max_market_cap > 0:
        params["max_market_cap"] = max_market_cap
    if min_dividend_yield > 0:
        params["min_dividend_yield"] = min_dividend_yield
    if filter_preset:
        params["filter_preset"] = filter_preset
    return await _call("/v1/finance/stock/screen", params)


@mcp.tool()
async def finance_search(
    keyword: str = "",
    type: str = "all",
    limit: int = 20,
) -> dict:
    """Search across 11,780+ securities: stocks, concepts, sectors, ETFs, indices.

    TYPE options:
    - stock: A-shares + Beijing Exchange + STAR Market (6,104 items)
    - concept: concept indices (2,222 items)
    - sector: industry/concept tree nodes (1,466 items)
    - etf: ETF funds (1,377 items)
    - index: major indices (613 items)
    - all: search all types at once

    Examples:
    - "芯片ETF" → finance_search(keyword="芯片", type="etf")
    - "AI概念" → finance_search(keyword="AI", type="concept")
    - "沪深300" → finance_search(keyword="沪深300", type="index")"""
    return await _call("/v1/finance/search", {"keyword": keyword, "type": type, "limit": limit})


# ---------------------------------------------------------------------------
# Info (3 tools)
# ---------------------------------------------------------------------------

@mcp.tool()
async def info_search(query: str, count: int = 10, recency: str = "noLimit") -> dict:
    """Search the web. Returns titles, links, and snippets.
    query: search keywords. count: number of results (1-50). recency: oneDay/oneWeek/oneMonth/oneYear/noLimit."""
    return await _call("/v1/info/search", {"q": query, "count": count, "recency": recency})


@mcp.tool()
async def info_scrape(url: str) -> dict:
    """Read a webpage and return its content as markdown.
    url: the webpage URL to scrape."""
    return await _call("/v1/info/scrape", {"url": url})


@mcp.tool()
async def info_news(category: str = "finance", limit: int = 20) -> dict:
    """Get latest news headlines.
    category: finance/general/tech/sports/... (default: finance). limit: number of articles (1-50)."""
    return await _call("/v1/info/news", {"category": category, "limit": limit})


# ---------------------------------------------------------------------------
# Life (3 tools)
# ---------------------------------------------------------------------------

@mcp.tool()
async def life_weather(city: str = "", location: str = "", forecast: bool = False) -> dict:
    """Get weather data: current conditions and optional 7-day forecast.
    city: city name (e.g. '北京'). location: lat,lng. forecast: include 7-day forecast."""
    params: dict = {"forecast": forecast}
    if city:
        params["city"] = city
    if location:
        params["location"] = location
    return await _call("/v1/life/weather", params)


@mcp.tool()
async def life_logistics(number: str, company: str = "") -> dict:
    """Track a courier package.
    number: tracking number. company: courier company code (auto-detected if omitted)."""
    params: dict = {"number": number}
    if company:
        params["company"] = company
    return await _call("/v1/life/logistics", params)


@mcp.tool()
async def life_ip(address: str = "") -> dict:
    """Get IP geolocation info.
    address: IP address (defaults to caller IP if omitted)."""
    params: dict = {}
    if address:
        params["address"] = address
    return await _call("/v1/life/ip", params)


def _init_telemetry() -> None:
    otel_enabled = os.getenv("OTEL_ENABLED", "").lower() in ("true", "1", "yes")
    otel_endpoint = os.getenv("OTEL_ENDPOINT", "")
    otel_instance_id = os.getenv("OTEL_INSTANCE_ID", "")
    otel_token = os.getenv("OTEL_TOKEN", "")

    if otel_enabled and otel_endpoint:
        from api.telemetry import setup_telemetry
        setup_telemetry(
            "groundapi-mcp",
            otel_endpoint=otel_endpoint,
            otel_instance_id=otel_instance_id,
            otel_token=otel_token,
        )


def main():
    _init_telemetry()

    parser = argparse.ArgumentParser(description="GroundAPI MCP Server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument(
        "--transport", default="stdio",
        choices=["streamable-http", "sse", "stdio"],
        help="MCP transport: stdio (default), sse, or stdio"
    )
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    elif args.transport == "sse":
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        mcp.run(transport="streamable-http", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
