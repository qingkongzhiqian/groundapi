"""
GroundAPI MCP Server — 11 tools for AI Agents.

Finance: 5 tools (stock, market, screen, search, gold price).
Info: 4 tools (search, news, trending, bulletin).
Life: 2 tools (weather, calendar).

Requires Bearer-token authentication: the client must supply its own
GroundAPI API Key via ``Authorization: Bearer sk_gapi_...``.
"""

import argparse
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
import httpx
from fastmcp import FastMCP
from fastmcp.server.auth import TokenVerifier
from fastmcp.server.auth.auth import AccessToken
from fastmcp.server.dependencies import get_access_token

_env_file = Path(__file__).resolve().parent.parent.parent / ".env"
if _env_file.exists():
    load_dotenv(_env_file)

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

logger = logging.getLogger("groundapi.mcp")


class ApiKeyVerifier(TokenVerifier):
    """Real authentication for the MCP server.

    Replaces the previous ``DebugTokenVerifier`` which only checked the
    ``sk_gapi_`` prefix. This verifier now runs the same DB-backed validation
    used by the REST API (``api.middleware.auth.validate_api_key``), so:

    * Forged tokens with the right prefix but no DB row are rejected at the
      MCP layer instead of being forwarded to backend (saves CPU/network).
    * Disabled keys (``is_active=False``) are rejected immediately.
    * Redis caching is reused — same hot-path latency as the REST API.
    * The configured ``INTERNAL_MCP_TOKEN`` keeps working so the
      ``ai_analyze`` round-trip (backend → MCP → backend) is unaffected.

    Returned ``AccessToken.client_id`` carries the user_id so tools that
    need per-user context can read it via ``get_access_token().client_id``.
    """

    async def verify_token(self, token: str) -> AccessToken | None:
        if not token:
            return None

        # Lazy import keeps module import cheap and avoids circular imports
        # while still letting us share the *exact* validation logic with the
        # REST API path.
        from api.database import AsyncSessionLocal
        from api.middleware.auth import validate_api_key
        from api.services.cache import get_redis

        try:
            redis = await get_redis()
            async with AsyncSessionLocal() as db:
                auth_info = await validate_api_key(token, db, redis)
                # validate_api_key may issue an UPDATE on api_keys.last_used_at;
                # commit so it actually lands. No-op when nothing was written.
                await db.commit()
        except Exception:
            logger.exception("ApiKeyVerifier failure during token validation")
            return None

        if auth_info is None:
            return None

        return AccessToken(
            token=token,
            client_id=auth_info["user_id"],
            scopes=[auth_info.get("plan") or "free"],
            expires_at=None,
        )


auth = ApiKeyVerifier()

mcp = FastMCP(
    "GroundAPI",
    auth=auth,
    instructions=(
        "One-stop data layer for AI Agents. "
        "Finance: A-share stock/index/ETF data (11 aspects), market overview (5 scopes), "
        "multi-dimensional screening, universal search across 11,780 securities, gold price. "
        "Info: web search, news, trending topics, daily bulletin. "
        "Life: weather, calendar (lunar/solar terms/holidays/trading days). "
        "Requires authentication: pass your GroundAPI API Key as a Bearer token."
    ),
)


async def _call(path: str, params: dict | None = None) -> dict:
    token = get_access_token()
    headers = {"Content-Type": "application/json", "X-API-Key": token.token}
    transport = httpx.AsyncHTTPTransport(proxy=None)
    async with httpx.AsyncClient(base_url=API_BASE, timeout=60, transport=transport) as client:
        resp = await client.get(path, params=params or {}, headers=headers)
        return resp.json()


# ---------------------------------------------------------------------------
# Finance (5 tools)
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
    """Query A-share securities (stocks/indices/ETFs). One stop for everything about a security.

    PICK ASPECTS BY USER INTENT (most → least common):
    - "How is XXX doing?" / quick look           → aspects="overview"  (DEFAULT, recommended)
    - "Show me the price / PE"                    → aspects="quote"
    - "Show me the K-line / chart / trend"        → aspects="quote,kline"
    - "Technical analysis / MACD / signals"       → aspects="quote,kline,technical"
    - "Earnings / financials / fundamentals"      → aspects="financial"
    - "Top shareholders / institutional holdings" → aspects="holders"
    - "Management team / executives"              → aspects="management"
    - "Dividends / unlocks / earnings forecast"   → aspects="events"
    - "Compare to peers / industry ranking"       → aspects="peers"
    - "Comprehensive analysis"                    → aspects="summary"  (combines quote+technical+financial+holders)

    SYMBOL FORMATS:
    - Stock:  "600519" or "600519.SH" or "000001.SZ"
    - Index:  "000001.SH" (上证), "399001.SZ" (深证), "399006.SZ" (创业板)
    - ETF:    "510300" or "510300.SH"
    - Multi-compare (up to 10): "600519,000858,601398" — returns side-by-side data
    - Search by name: keyword="贵州茅台" — returns matching codes (no aspects needed)

    OTHER PARAMS:
    - days: lookback window for kline/technical (1-500, default 60)
    - period: "d" daily / "w" weekly / "m" monthly (minute K not supported)
    - limit: max results when using keyword search (1-50)

    NOTES:
    - Data updates after market close (~15:35 CST). Not real-time intraday.
    - Always try aspects="overview" first; only request more aspects when needed.
    - Combine multiple aspects in ONE call; don't make multiple calls."""
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
    """Market-wide A-share data — for "what's happening in the market" questions.

    PICK SCOPE BY USER INTENT:
    - "How is the market today?" / "大盘怎么样"     → scope="overview"  (DEFAULT)
    - "Limit-up stocks today" / "今天涨停的"         → scope="hot"
    - "Strongest stocks" / "最强势的股"              → scope="signals"
    - "Sector rotation" / "板块涨跌"                 → scope="sectors"
    - "Constituent stocks of AI" / "AI 概念成分股"   → scope="sectors", sector="AI"
    - "New IPO calendar" / "新股日历"                → scope="ipo"

    Combine multiple scopes for daily briefing-style requests:
    - "Daily market briefing"  → scope="overview,hot,signals"

    SCOPE DETAILS:
    - overview: 5 major indices (SSE/SZSE/ChiNext/STAR50/BSE50) + sentiment counters
    - hot: 5 stock pools (limit-up/down/strong/failed-limit/sub-new) with streak tiers
    - sectors: concept & industry rankings; pass `sector` param to drill into constituents
    - ipo: upcoming new stock subscriptions calendar
    - signals: multi-streak limit-ups + high-gain stocks (>15% intraday)

    OTHER PARAMS:
    - sector: only used with scope="sectors" to drill down (e.g. "AI", "半导体", "光伏")
    - date: YYYY-MM-DD, defaults to today (use historical date for past pools)
    - limit: max results per pool (1-100, default 20)"""
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
    """Find stocks matching user criteria. ALL params optional — combine 1-3 you need.

    COMMON USE CASES (most → least common):
    - "高分红银行股"        → finance_screen(industry="银行", min_dividend_yield=3)
    - "白酒龙头"            → finance_screen(industry="食品饮料", sort_by="market_cap", limit=10)
    - "AI 概念股"           → finance_screen(concept="AI")
    - "低估值蓝筹"          → finance_screen(filter_preset="large_cap_stable")
    - "中小盘成长股"        → finance_screen(filter_preset="small_cap_growth")
    - "高股息低 PE"         → finance_screen(filter_preset="low_pe_high_div")
    - "今日涨幅榜"          → finance_screen()  (no filters = top by change_pct)
    - "PE < 15 的股票"      → finance_screen(pe_max=15)
    - "市值超千亿的股票"    → finance_screen(min_market_cap=100000000000)

    PARAMS (units: market_cap in CNY, dividend_yield in %):
    - industry: free text match (e.g. "银行", "电子", "医药")
    - concept: free text match (e.g. "AI", "半导体", "新能源")
    - pe_min / pe_max / pb_max: valuation filters
    - min_market_cap / max_market_cap: market cap range in CNY
    - min_dividend_yield: minimum dividend yield in %
    - filter_preset: shortcut to combine common filters (see below)
    - sort_by: change_pct/pe/pb/market_cap/turnover_rate/dividend_yield/volume
    - order: desc / asc
    - limit: 1-100, default 20

    FILTER PRESETS:
    - low_pe_high_div:    PE<15 AND dividend yield>3%   (value/dividend stocks)
    - small_cap_growth:   market cap<10B                (small-cap growth)
    - large_cap_stable:   market cap>50B AND PE<20      (blue chip)

    TIP: industry vs concept — industry is GICS-style fixed taxonomy ("银行", "医药"),
         concept is theme-based ("AI", "国资", "数据要素"). Use whichever fits the query."""
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
    """Find a security by name or partial code. Use this to RESOLVE A NAME TO A CODE
    before calling finance_stock with that code.

    WHEN TO USE THIS:
    - User says a name not a code → "茅台" → search → get "600519"
    - User asks "what ETFs cover XXX" → search type="etf"
    - User asks "what's in XXX concept" → search type="concept"
    - You're not sure what code to pass to finance_stock

    TYPE PICKING:
    - type="all" (DEFAULT): search across all 5 types — fine for ambiguous queries
    - type="stock": individual stocks (A-share + 北交所 + 科创板, 6,104 items)
    - type="concept": theme indices ("AI", "数据要素", "光伏", 2,222 items)
    - type="sector": industry/concept tree nodes (1,466 items)
    - type="etf": ETF funds (1,377 items)
    - type="index": broad market indices ("沪深300", "中证500", 613 items)

    EXAMPLES:
    - "茅台" / "比亚迪"          → finance_search(keyword="茅台")
    - "芯片 ETF"                 → finance_search(keyword="芯片", type="etf")
    - "AI 概念有哪些股票"        → finance_search(keyword="AI", type="concept")
    - "沪深300 / 标普500 指数"   → finance_search(keyword="沪深300", type="index")

    NOTE: this only RESOLVES code/name — to get actual quote data, pass the resolved
    code to finance_stock(symbol="...")."""
    return await _call("/v1/finance/search", {"keyword": keyword, "type": type, "limit": limit})


# ---------------------------------------------------------------------------
# Info (4 tools)
# ---------------------------------------------------------------------------

@mcp.tool()
async def info_search(query: str, count: int = 10, recency: str = "noLimit") -> dict:
    """Search the web in real time — for finding recent news, articles, research.

    WHEN TO USE:
    - User asks about a recent event, company news, industry research
    - You need to look up something not in your training data
    - Combine with finance_stock to enrich a stock query with latest news

    EXAMPLES:
    - "最近 AI 行业的新闻"     → info_search(query="AI 行业最新动态", recency="oneWeek")
    - "茅台最近发生了什么"     → info_search(query="贵州茅台 最新消息", recency="oneMonth")

    PARAMS:
    - query: search keywords (max 70 chars)
    - count: number of results (1-50, default 10)
    - recency: oneDay / oneWeek / oneMonth / oneYear / noLimit (default noLimit)"""
    return await _call("/v1/info/search", {"q": query, "count": count, "recency": recency})


@mcp.tool()
async def info_news(category: str = "finance", limit: int = 20) -> dict:
    """Get curated news headlines by category. Pre-categorized; faster than search.

    WHEN TO USE:
    - User asks "今天有什么新闻" / "最新财经新闻"
    - You need a quick news roundup without specifying a topic
    - For specific company/event news, prefer info_search instead

    CATEGORIES:
    - finance (DEFAULT) / general / tech / sports / military / entertainment
    - fashion / travel / education / health / food / auto / game / house

    EXAMPLES:
    - "今天的财经新闻"       → info_news(category="finance")
    - "科技新闻"             → info_news(category="tech", limit=10)

    PARAMS:
    - category: see list above (default: finance)
    - limit: number of articles (1-50, default 20)"""
    return await _call("/v1/info/news", {"category": category, "limit": limit})


# ---------------------------------------------------------------------------
# Life (2 tools)
# ---------------------------------------------------------------------------

@mcp.tool()
async def life_weather(city: str = "", location: str = "", forecast: bool = False) -> dict:
    """Get current weather and optional 7-day forecast.

    WHEN TO USE:
    - "今天 XXX 天气" / "北京天气怎么样"      → city="北京"
    - "未来一周天气"                          → city="北京", forecast=True
    - GPS coordinates from a device           → location="39.9,116.4"

    PARAMS:
    - city: city name in Chinese or English (北京 / Beijing / 上海 / Shanghai)
    - location: "lat,lng" GPS coordinates (alternative to city)
    - forecast: True to include 7-day forecast"""
    params: dict = {"forecast": forecast}
    if city:
        params["city"] = city
    if location:
        params["location"] = location
    return await _call("/v1/life/weather", params)


@mcp.tool()
async def life_calendar(date: str = "") -> dict:
    """Calendar info: lunar date, solar terms, holidays, trading day status.

    WHEN TO USE:
    - "今天农历多少" / "明天是什么节气"
    - "今天是不是交易日"   ← MOST COMMON USE: check if A-share market is open
    - "五一放几天假"
    - You need to confirm market open/close before showing stock data

    PARAMS:
    - date: YYYY-MM-DD format. Defaults to today if omitted.

    RETURNS includes: lunar date, nearest solar terms, holiday/workday status,
    is_trading_day flag, next trading day (if market is closed today)."""
    params: dict = {}
    if date:
        params["date"] = date
    return await _call("/v1/life/calendar", params)


# ---------------------------------------------------------------------------
# Finance — gold price
# ---------------------------------------------------------------------------

@mcp.tool()
async def finance_gold_price() -> dict:
    """Latest gold and precious metal spot prices (Au/Ag/Pt). No params required.

    WHEN TO USE:
    - "金价多少" / "黄金价格"
    - Macro context for risk-off sentiment
    - Comparing precious metals (gold/silver/platinum)"""
    return await _call("/v1/finance/gold-price")


# ---------------------------------------------------------------------------
# Info — extra tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def info_trending() -> dict:
    """Get trending topics from major Chinese platforms (微博/抖音/知乎). No params.

    WHEN TO USE:
    - "今天什么话题最火" / "热搜榜"
    - You need overall public sentiment / what people are talking about
    - Sanity check whether a stock-related event is trending publicly"""
    return await _call("/v1/info/trending")


@mcp.tool()
async def info_bulletin() -> dict:
    """Daily morning news briefing — concise digest of important events. No params.

    WHEN TO USE:
    - "今天的早报" / "每日简报"
    - User wants a quick "what's happening today" summary
    - Faster than info_news; pre-curated by editors"""
    return await _call("/v1/info/bulletin")


def main():
    logfire_token = os.getenv("LOGFIRE_TOKEN", "")
    if logfire_token:
        import logfire
        logfire.configure(
            token=logfire_token,
            service_name="groundapi-mcp",
            service_version="3.0.0",
        )
        logfire.instrument_httpx()

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
