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
    """Look up individual A-share stock data — search by name, get real-time quotes, pull historical prices, or retrieve technicals/fundamentals for a single stock.

    Use this tool when the user asks about a specific stock (by name or symbol code).
    Do NOT use this tool for screening multiple stocks by criteria — use finance_stock_screen instead.
    Do NOT use this tool for broad market or sector overviews — use finance_market instead.

    Modes:
    - Search by name: finance_stock(keyword="茅台") → returns matching stocks with basic info.
    - Latest quote: finance_stock(symbol="600519") → current price, change, PE, PB, dividend yield.
    - Specific date: finance_stock(symbol="600519", date="2026-03-28") → quote on that date.
    - Historical: finance_stock(symbol="600519", days=60) → last N trading-day OHLCV records.
    - With technicals: finance_stock(symbol="600519", days=60, include="technicals") → adds MA, MACD, RSI.
    - With fundamentals: finance_stock(symbol="600519", include="fundamental") → adds PE, PB, ROE, revenue.

    Returns a JSON dict with a "data" key. The shape depends on the mode used.

    Args:
        keyword: Stock name or partial code to search. Mutually exclusive with symbol.
        symbol: 6-digit A-share stock code (e.g. "600519"). Mutually exclusive with keyword.
        date: Specific trading date in YYYY-MM-DD format. Only used with symbol.
        days: Number of recent trading days of history to return (1-250). 0 means latest only.
        include: Comma-separated extras — "technicals" and/or "fundamental". Only used with symbol.
        indicators: Technical indicator list (default "ma,macd,rsi"). Only used when include contains "technicals".
        limit: Max results when searching by keyword (1-50, default 10)."""
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
    """Screen and rank multiple A-share stocks by financial criteria — filter by industry, PE, PB, market cap, or dividend yield, and sort the results.

    Use this tool when the user wants to find stocks matching specific criteria or see top/bottom rankings (e.g. biggest gainers, cheapest PE).
    Do NOT use this tool for a single stock lookup — use finance_stock instead.
    Do NOT use this tool for market-level or sector-level summaries — use finance_market instead.

    Returns a JSON dict with a "data" list of stock objects, each containing symbol, name, price, change_pct, and the requested metrics.

    Args:
        industry: Filter by industry name in Chinese (e.g. "半导体", "白酒"). Empty means all industries.
        pe_max: Maximum PE ratio (0 means no upper limit).
        pe_min: Minimum PE ratio (0 means no lower limit).
        pb_max: Maximum PB ratio (0 means no upper limit).
        min_market_cap: Minimum market cap in 亿元 (0 means no limit).
        max_market_cap: Maximum market cap in 亿元 (0 means no limit).
        min_dividend_yield: Minimum dividend yield in percent (0 means no limit).
        sort_by: Field to sort results — "change_pct", "pe", "pb", "market_cap", "dividend_yield", "turnover" (default "change_pct").
        order: Sort direction — "desc" or "asc" (default "desc").
        limit: Number of results to return (1-100, default 20)."""
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
    """Get A-share market-level data — major index quotes, market breadth, volume, and optionally sector rankings, fund flows, valuation maps, or macro indicators.

    Use this tool when the user asks about the overall market, sector performance, or macro-economic conditions.
    Use the sector param to drill into one specific sector and see its constituent stocks.
    Do NOT use this tool for individual stock queries — use finance_stock instead.
    Do NOT use this tool for stock screening/filtering — use finance_stock_screen instead.

    Returns a JSON dict with "overview" (indices, breadth, volume) plus optional keys depending on include/sector params.

    Args:
        date: Trading date in YYYY-MM-DD format. Empty means the latest trading day.
        include: Comma-separated extras to append — "sectors", "funds", "valuation", "macro", or combinations like "sectors,macro".
        sector: Specific sector name in Chinese (e.g. "半导体") to get that sector's detail and constituent stocks. Overrides include.
        type: Sector classification — "industry" or "concept" (default "industry").
        sort_by: Sort field for sector/constituent lists — "change_pct", "market_cap", etc. (default "change_pct").
        limit: Max items in sector/constituent lists (1-100, default 20)."""
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
    """Search, view details of, or rank Chinese public funds (公募基金) — ETFs, index funds, bond funds, etc.

    Use this tool when the user asks about a specific fund, wants to find funds by name, or wants fund performance rankings.
    Do NOT use this tool for stock data — use finance_stock or finance_stock_screen instead.

    Returns a JSON dict with a "data" key — a list of fund objects (search/ranking) or a single fund detail object.

    Args:
        keyword: Fund name or partial code to search (e.g. "沪深300", "110011"). Empty for ranking mode.
        code: Exact fund code for detail view (e.g. "110011"). Returns NAV history, manager info, and holdings.
        fund_type: Filter by type — "equity", "bond", "index", "hybrid", "money", "qdii". Empty means all.
        sort_by: Ranking field — "perf_ytd", "return_1y", "return_3y", "nav", "size" (default "perf_ytd").
        order: Sort direction — "desc" or "asc" (default "desc").
        limit: Number of results (1-100, default 20). Ignored when code is provided."""
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
    """Search the web using multiple search engines and return a list of results with titles, URLs, and text snippets.

    Use this tool when the user needs to find information on the internet — news, articles, documentation, etc.
    Do NOT use this tool to read full page content — use info_scrape on a specific URL instead.
    Do NOT use this tool for structured news feeds — use info_news instead.

    Returns a JSON dict with a "results" list, each containing "title", "url", and "snippet".

    Args:
        query: Search keywords or question (required, non-empty string).
        count: Number of results to return (1-50, default 10).
        recency: Time filter — "oneDay", "oneWeek", "oneMonth", "oneYear", or "noLimit" (default "noLimit")."""
    return await _call("/v1/info/search", {"q": query, "count": count, "recency": recency})


@mcp.tool()
async def info_scrape(url: str) -> dict:
    """Fetch a single webpage and extract its main content as clean Markdown text, stripping navigation, ads, and boilerplate.

    Use this tool when the user wants to read or analyze a specific webpage's content.
    Do NOT use this tool to search for pages — use info_search first to find relevant URLs.

    Returns a JSON dict with "title", "content" (Markdown string), and "url".

    Args:
        url: Full URL of the webpage to scrape (required, must start with http:// or https://)."""
    return await _call("/v1/info/scrape", {"url": url})


@mcp.tool()
async def info_news(category: str = "finance", limit: int = 20) -> dict:
    """Get the latest news headlines organized by category, returning titles, sources, publish times, and URLs.

    Use this tool when the user asks for recent news or trending topics in a specific category.
    Do NOT use this tool for searching a specific topic — use info_search instead.
    Do NOT use this tool to read a full article — use info_scrape with the article URL instead.

    Returns a JSON dict with a "data" list of article objects, each containing "title", "source", "time", and "url".

    Args:
        category: News category — "finance", "general", "tech", "sports", "entertainment", "world" (default "finance").
        limit: Number of articles to return (1-50, default 20)."""
    return await _call("/v1/info/news", {"category": category, "limit": limit})


# ---------------------------------------------------------------------------
# Life (3 tools)
# ---------------------------------------------------------------------------

@mcp.tool()
async def life_weather(city: str = "", location: str = "", forecast: bool = False) -> dict:
    """Get current weather conditions and optionally a 7-day forecast for a city or geographic coordinate.

    Use this tool when the user asks about weather, temperature, humidity, wind, or forecasts.
    Do NOT use this tool for non-weather location info — use life_ip for IP-based geolocation.

    Returns a JSON dict with "current" (temperature, humidity, wind, condition) and optionally "forecast" (7-day array).

    Args:
        city: City name in Chinese or English (e.g. "北京", "Tokyo"). Provide either city or location.
        location: Geographic coordinates as "lat,lng" (e.g. "39.9,116.4"). Provide either city or location.
        forecast: If true, include a 7-day daily forecast in the response (default false)."""
    params: dict = {"forecast": forecast}
    if city:
        params["city"] = city
    if location:
        params["location"] = location
    return await _call("/v1/life/weather", params)


@mcp.tool()
async def life_logistics(number: str, company: str = "") -> dict:
    """Track a courier/express package and return its delivery status and tracking history.

    Use this tool when the user provides a tracking number and wants to know the package status.
    Do NOT use this tool without a tracking number — it cannot search for packages by other criteria.

    Returns a JSON dict with "company", "status" (e.g. "in_transit", "delivered"), and "traces" (chronological list of tracking events).

    Args:
        number: Package tracking number (required, e.g. "SF1234567890").
        company: Courier company code (e.g. "sf", "yd", "zt"). Auto-detected from tracking number format if omitted."""
    params: dict = {"number": number}
    if company:
        params["company"] = company
    return await _call("/v1/life/logistics", params)


@mcp.tool()
async def life_ip(address: str = "") -> dict:
    """Look up geolocation information for an IP address — country, region, city, timezone, and ISP.

    Use this tool when the user asks where an IP address is located or wants to know their own IP info.
    Do NOT use this tool for weather data — use life_weather instead.

    Returns a JSON dict with "ip", "country", "region", "city", "timezone", "isp", and "lat"/"lng".

    Args:
        address: IPv4 or IPv6 address to look up (e.g. "8.8.8.8"). If omitted, returns info for the caller's IP."""
    params: dict = {}
    if address:
        params["address"] = address
    return await _call("/v1/life/ip", params)


def _init_telemetry() -> None:
    otel_enabled = os.getenv("OTEL_ENABLED", "").lower() in ("true", "1", "yes")
    otel_endpoint = os.getenv("OTEL_ENDPOINT", "")
    otel_token = os.getenv("OTEL_TOKEN", "")

    if otel_enabled and otel_endpoint:
        from api.telemetry import setup_telemetry
        setup_telemetry(
            "groundapi-mcp",
            otel_endpoint=otel_endpoint,
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
