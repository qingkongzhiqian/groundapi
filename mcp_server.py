"""
GroundAPI MCP Server — 10 tools for AI Agents.
Reads API key from GROUNDAPI_API_KEY environment variable.
"""

import argparse
import os

import httpx
from fastmcp import FastMCP

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("GROUNDAPI_API_KEY", "")

mcp = FastMCP(
    "GroundAPI",
    instructions=(
        "One-stop data layer for AI Agents. "
        "Finance: A-share stock quotes, market overview, sector analysis, "
        "fund data, macro indicators. "
        "Info: web search, news, webpage scraping. "
        "Life: weather, logistics tracking, IP geolocation. "
        "API key is configured server-side — no need to pass it per tool call."
    ),
)


def _headers() -> dict:
    h = {"Content-Type": "application/json"}
    if API_KEY:
        h["X-API-Key"] = API_KEY
    return h


async def _call(path: str, params: dict | None = None) -> dict:
    async with httpx.AsyncClient(base_url=API_BASE, timeout=60) as client:
        resp = await client.get(path, params=params or {}, headers=_headers())
        return resp.json()


# ---------------------------------------------------------------------------
# Finance (5 tools)
# ---------------------------------------------------------------------------

@mcp.tool()
async def finance_stock(
    keyword: str = "",
    symbol: str = "",
    date: str = "",
    days: int = 0,
    include: str = "",
    indicators: str = "ma,macd,rsi",
    limit: int = 10,
) -> dict:
    """Query one A-share stock or search the universe by keyword (China listed equities only).

    Use when: you need a single stock's quote, a trading day's OHLC, history, technicals, or
    fundamentals. Use keyword= for discovery; use symbol= (e.g. 600519) for a known code.

    Do not use for: multi-stock screens or top/bottom rankings (use finance_stock_screen);
    whole-market indices, sectors, or macro (use finance_market); funds (use finance_fund).

    Parameters: keyword — name/code fragment; symbol — ticker; date — YYYY-MM-DD; days — lookback
    trading days when >0; include — e.g. technicals, fundamental; indicators — comma list when
    technicals requested; limit — max matches for keyword search. Requires keyword or symbol."""
    params: dict = {}
    if keyword:
        params["keyword"] = keyword
        params["limit"] = limit
    if symbol:
        params["symbol"] = symbol
    if date:
        params["date"] = date
    if days > 0:
        params["days"] = days
    if include:
        params["include"] = include
        params["indicators"] = indicators
    return await _call("/v1/finance/stock", params)


@mcp.tool()
async def finance_stock_screen(
    industry: str = "",
    pe_max: float = 0,
    pe_min: float = 0,
    pb_max: float = 0,
    min_market_cap: float = 0,
    max_market_cap: float = 0,
    min_dividend_yield: float = 0,
    sort_by: str = "change_pct",
    order: str = "desc",
    limit: int = 20,
) -> dict:
    """Screen many A-share stocks by filters, or return ranked lists (e.g. movers).

    Use when: you need a list of tickers matching valuation/size/yield constraints, or a
    leaderboard sorted by change_pct or similar. All filters are optional; omit filters for a
    default ranking.

    Do not use for: deep data on one ticker (use finance_stock); market-wide dashboard (use
    finance_market).

    Parameters: industry — sector name; pe_max/pe_min/pb_max — valuation bounds; min/max_market_cap;
    min_dividend_yield; sort_by — ranking field; order — asc|desc; limit — max rows."""
    params: dict = {"sort_by": sort_by, "order": order, "limit": limit}
    if industry:
        params["industry"] = industry
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
    return await _call("/v1/finance/stock/screen", params)


@mcp.tool()
async def finance_market(
    date: str = "",
    include: str = "",
    sector: str = "",
    type: str = "industry",
    sort_by: str = "change_pct",
    limit: int = 20,
) -> dict:
    """Get market data. Supports multiple modes:
    - Market overview: finance_market() — indices, breadth, volume, top sectors, macro
    - With sectors: finance_market(include="sectors") — add sector ranking
    - With funds: finance_market(include="funds") — add fund ranking
    - With valuation: finance_market(include="valuation") — add industry valuation map
    - With macro: finance_market(include="macro") — add macro indicators
    - All extras: finance_market(include="sectors,funds,valuation,macro")
    - Sector detail: finance_market(sector="半导体") — specific sector with constituents"""
    params: dict = {"type": type, "sort_by": sort_by, "limit": limit}
    if date:
        params["date"] = date
    if include:
        params["include"] = include
    if sector:
        params["sector"] = sector
    return await _call("/v1/finance/market", params)


@mcp.tool()
async def finance_fund(
    keyword: str = "",
    code: str = "",
    fund_type: str = "",
    sort_by: str = "perf_ytd",
    order: str = "desc",
    limit: int = 20,
) -> dict:
    """Query fund data: search, detail, or ranking.
    - Search: finance_fund(keyword="沪深300")
    - Detail: finance_fund(code="110011")
    - Ranking: finance_fund(sort_by="return_1y", limit=20)"""
    params: dict = {"sort_by": sort_by, "order": order, "limit": limit}
    if keyword:
        params["keyword"] = keyword
    if code:
        params["code"] = code
    if fund_type:
        params["fund_type"] = fund_type
    return await _call("/v1/finance/fund", params)



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
