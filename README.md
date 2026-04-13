<p align="center">
  <h1 align="center">GroundAPI</h1>
  <p align="center"><strong>Real-time Data API for AI Agents</strong></p>
  <p align="center">
    <a href="https://groundapi.net">Website</a> · <a href="https://docs.groundapi.net">Docs</a> · <a href="https://mcp.groundapi.net/mcp">MCP Endpoint</a> · <a href="https://pypi.org/project/groundapi-cli/">CLI</a>
  </p>
  <p align="center">
    <a href="./README_zh.md">中文</a> | English
  </p>
</p>

---

GroundAPI provides a unified data layer for AI Agents — **18 tools** across finance, information, and life services. One API key, three access methods: **REST API**, **MCP**, and **CLI**.

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://mcp.groundapi.net/mcp)
[![PyPI](https://img.shields.io/pypi/v/groundapi-cli.svg)](https://pypi.org/project/groundapi-cli/)

## Table of Contents

- [Quick Start](#quick-start)
- [MCP Tools Reference](#mcp-tools-reference)
  - [Finance (6 tools)](#finance-6-tools)
  - [Information (5 tools)](#information-5-tools)
  - [Life Services (7 tools)](#life-services-7-tools)
- [REST API](#rest-api)
- [CLI Reference](#cli-reference)
- [Agent Skills](#agent-skills)
- [Self-hosted MCP Server](#self-hosted-mcp-server)
- [Pricing](#pricing)

## Quick Start

Get your API key at [groundapi.net](https://groundapi.net) — **500 free calls/month**, no credit card required.

### Option 1: MCP (recommended for AI Agents)

Add to Claude Desktop, Cursor, Windsurf, or any MCP-compatible client:

```json
{
  "mcpServers": {
    "groundapi": {
      "url": "https://mcp.groundapi.net/mcp",
      "headers": {
        "X-API-Key": "YOUR_API_KEY"
      }
    }
  }
}
```

### Option 2: REST API

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
  "https://api.groundapi.net/v1/finance/stock?symbol=600519&aspects=overview"
```

### Option 3: CLI

```bash
pip install groundapi-cli
groundapi config set-key YOUR_API_KEY
groundapi stock --symbol 600519
```

---

## MCP Tools Reference

### Finance (6 tools)

#### `finance_stock` — Securities Data

All-in-one query for A-share stocks, indices, and ETFs. Supports **13 data dimensions** and multi-stock comparison.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbol` | string | — | Stock code. Comma-separated for comparison (e.g. `"600519,000858"`) |
| `keyword` | string | — | Search by name (e.g. `"茅台"`) |
| `aspects` | string | `"overview"` | Data dimensions, comma-separated (see table below) |
| `days` | int | `60` | History range for kline/technical |
| `period` | string | `"d"` | K-line period: `5/15/30/60/d/w/m` |

**13 Available Aspects:**

| Aspect | Returns | Use When |
|--------|---------|----------|
| `overview` | Quick snapshot: quote + profile brief + financial brief | "How's XXXX doing?" |
| `profile` | Full company info, concepts, index membership, capital structure | "What does this company do?" |
| `quote` | Real-time price, PE/PB, 5-level bid/ask, limit up/down distance | "Current price?" |
| `kline` | K-line data (supports 5/15/30/60min, daily, weekly, monthly) | "Show me the chart" |
| `technical` | MACD, MA, BOLL, KDJ + signal detection (e.g. "DIF crosses above DEA") | "Technical analysis?" |
| `financial` | 3 financial statements, quarterly P&L, cash flow, dividends, forecasts | "How are the financials?" |
| `flow` | Capital flow (mega/large/medium/small orders), consecutive inflow/outflow | "Is smart money buying?" |
| `holders` | Top 10 shareholders, float holders, count trend, fund holdings | "Who are the major shareholders?" |
| `management` | Executives, board directors, supervisors | "Who's the management?" |
| `events` | Dividends, share issuance, lock-up expiry, earnings calendar | "When's the next dividend?" |
| `tick` | Intraday tick-by-tick with buy/sell direction stats | "More buyers or sellers today?" |
| `summary` | Multi-dimensional factual aggregation (no opinions) | "Give me a full data summary" |
| `peers` | Same-industry comparison table with PE/PB/market cap ranking | "How does it rank in the sector?" |

```python
# Quick overview
finance_stock(symbol="600519")

# Deep dive with multiple aspects
finance_stock(symbol="600519", aspects="quote,technical,financial,flow")

# Search by name
finance_stock(keyword="平安")

# Compare multiple stocks
finance_stock(symbol="601398,601939,600036", aspects="quote")

# Index / ETF
finance_stock(symbol="000001.SH", aspects="kline,technical")  # SSE Composite
finance_stock(symbol="510300", aspects="quote")                # CSI 300 ETF
```

#### `finance_market` — Market Overview

Market-wide data: major indices, hot stocks, sector rotation, IPO calendar, anomaly signals.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `scope` | string | `"overview"` | Data scope, comma-separated |
| `sector` | string | — | Drill into a specific sector |
| `date` | string | — | Date filter (YYYY-MM-DD) |

**Scopes:** `overview` (indices + sentiment) · `hot` (limit-up/down pools, streak breakdown) · `sectors` (concept & industry lists) · `ipo` (IPO calendar) · `signals` (anomaly detection)

```python
finance_market()                                    # Today's market
finance_market(scope="hot")                         # Limit-up/down stocks
finance_market(scope="sectors", sector="AI")        # AI sector constituents
finance_market(scope="ipo")                         # IPO calendar
```

#### `finance_screen` — Stock Screener

Multi-criteria screening with 20+ dimensions and preset filter combinations.

| Parameter | Type | Description |
|-----------|------|-------------|
| `industry` | string | Industry filter (e.g. `"银行"`, `"半导体"`) |
| `concept` | string | Concept filter (e.g. `"AI"`, `"新能源"`) |
| `pe_max` / `pe_min` | float | PE ratio range |
| `pb_max` | float | Max PB ratio |
| `min_market_cap` / `max_market_cap` | float | Market cap range |
| `min_dividend_yield` | float | Min dividend yield (%) |
| `filter_preset` | string | `low_pe_high_div` · `small_cap_growth` · `large_cap_stable` |
| `sort_by` | string | Sort field (default: `change_pct`) |

```python
finance_screen(industry="银行", pe_max=10)                       # Low-PE bank stocks
finance_screen(min_dividend_yield=3, sort_by="dividend_yield")   # High dividend
finance_screen(concept="AI")                                      # AI concept stocks
finance_screen(filter_preset="low_pe_high_div")                  # Preset: value picks
```

#### `finance_search` — Universal Search

Search across **11,780+ securities**: stocks, concepts, sectors, ETFs, indices.

| Parameter | Type | Description |
|-----------|------|-------------|
| `keyword` | string | Search query |
| `type` | string | `all` · `stock` (6,104) · `concept` (2,222) · `sector` (1,466) · `etf` (1,377) · `index` (613) |

```python
finance_search(keyword="芯片", type="etf")        # Chip ETFs
finance_search(keyword="AI", type="concept")       # AI concept indices
finance_search(keyword="沪深300", type="index")    # CSI 300
```

#### `finance_exchange_rate` — Currency Exchange

```python
finance_exchange_rate(from_currency="USD", to_currency="CNY")
finance_exchange_rate(from_currency="EUR", to_currency="JPY")
```

#### `finance_gold_price` — Precious Metals

```python
finance_gold_price()   # Gold, silver, platinum real-time prices
```

---

### Information (5 tools)

#### `info_search` — Web Search

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Search keywords |
| `count` | int | Number of results (1–50, default 10) |
| `recency` | string | `noLimit` · `oneDay` · `oneWeek` · `oneMonth` · `oneYear` |

```python
info_search(query="AI Agent trends 2026", count=20, recency="oneWeek")
```

#### `info_scrape` — Web Scraper

```python
info_scrape(url="https://example.com")   # Returns clean markdown
```

#### `info_news` — News Headlines

| Parameter | Type | Description |
|-----------|------|-------------|
| `category` | string | `finance` · `general` · `tech` · `sports` ... |
| `limit` | int | Number of articles (1–50) |

```python
info_news(category="finance", limit=10)
info_news(category="tech")
```

#### `info_trending` — Trending Topics

Real-time hot search rankings from Weibo, Douyin, Zhihu, and more.

```python
info_trending()
```

#### `info_bulletin` — Daily Briefing

```python
info_bulletin()   # Morning news digest
```

---

### Life Services (7 tools)

#### `life_weather` — Weather

| Parameter | Type | Description |
|-----------|------|-------------|
| `city` | string | City name (e.g. `"Beijing"`) |
| `location` | string | Lat,lng (e.g. `"39.9,116.4"`) |
| `forecast` | bool | Include 7-day forecast |

```python
life_weather(city="北京", forecast=True)
life_weather(location="39.9,116.4")
```

#### `life_logistics` — Package Tracking

```python
life_logistics(number="SF1234567890")              # Auto-detect carrier
life_logistics(number="1234567890", company="yt")   # Specify carrier
```

#### `life_ip` — IP Geolocation

```python
life_ip(address="8.8.8.8")   # Country, city, timezone, ISP
life_ip()                     # Caller's IP
```

#### `life_tax` — Income Tax Calculator

```python
life_tax(monthly_salary=20000, insurance=2000, special_deduction=1500)
```

#### `life_calendar` — Calendar & Trading Days

```python
life_calendar()                  # Today: lunar date, solar terms, holiday, trading day
life_calendar(date="2026-05-01") # Specific date
```

#### `life_oil_price` — Fuel Prices

```python
life_oil_price()                  # National average
life_oil_price(province="北京")   # Province-specific
```

#### `life_traffic` — Driving Restrictions

```python
life_traffic(city="北京")   # Today's restricted plate numbers
```

---

## REST API

Base URL: `https://api.groundapi.net`

All endpoints require `X-API-Key` header.

| Endpoint | Description |
|----------|-------------|
| `GET /v1/finance/stock` | Stock/index/ETF data |
| `GET /v1/finance/market` | Market overview |
| `GET /v1/finance/stock/screen` | Stock screening |
| `GET /v1/finance/search` | Securities search |
| `GET /v1/finance/exchange-rate` | Exchange rates |
| `GET /v1/finance/gold-price` | Gold & precious metals |
| `GET /v1/info/search` | Web search |
| `GET /v1/info/scrape` | Web scraping |
| `GET /v1/info/news` | News headlines |
| `GET /v1/info/trending` | Trending topics |
| `GET /v1/info/bulletin` | Daily briefing |
| `GET /v1/life/weather` | Weather |
| `GET /v1/life/logistics` | Package tracking |
| `GET /v1/life/ip` | IP geolocation |
| `GET /v1/life/tax` | Tax calculator |
| `GET /v1/life/calendar` | Calendar info |
| `GET /v1/life/oil-price` | Fuel prices |
| `GET /v1/life/traffic` | Driving restrictions |

```bash
# Stock overview
curl -H "X-API-Key: YOUR_KEY" \
  "https://api.groundapi.net/v1/finance/stock?symbol=600519&aspects=overview"

# Multi-aspect deep dive
curl -H "X-API-Key: YOUR_KEY" \
  "https://api.groundapi.net/v1/finance/stock?symbol=600519&aspects=quote,technical,financial"

# Market overview
curl -H "X-API-Key: YOUR_KEY" \
  "https://api.groundapi.net/v1/finance/market?scope=overview"

# Stock screening
curl -H "X-API-Key: YOUR_KEY" \
  "https://api.groundapi.net/v1/finance/stock/screen?industry=银行&pe_max=10"

# Web search
curl -H "X-API-Key: YOUR_KEY" \
  "https://api.groundapi.net/v1/info/search?q=AI+Agent&count=10"

# Weather
curl -H "X-API-Key: YOUR_KEY" \
  "https://api.groundapi.net/v1/life/weather?city=北京&forecast=true"
```

Full API documentation: [docs.groundapi.net](https://docs.groundapi.net)

---

## CLI Reference

### Install

```bash
pip install groundapi-cli
groundapi config set-key YOUR_API_KEY
```

### Finance

```bash
# Stock quotes
groundapi stock --symbol 600519                            # Real-time quote
groundapi stock --keyword 贵州茅台                          # Search by name
groundapi stock --symbol 600519 --date 2024-12-31          # Specific date
groundapi stock --symbol 600519 --days 30                  # Last 30 days
groundapi stock --symbol 600519 --days 30 --include technicals  # With technicals

# Screening
groundapi screen                                           # Default ranking
groundapi screen --industry 白酒 --pe-max 30               # Industry + PE filter
groundapi screen --sort-by total_market_cap --limit 10     # Top 10 by market cap

# Market overview
groundapi market                                           # Indices + macro
groundapi market --include sectors,valuation               # With sectors + valuation
groundapi market --sector 半导体 --type industry           # Sector drill-down

# Funds
groundapi fund                                             # Fund ranking
groundapi fund --keyword 沪深300                            # Search funds
groundapi fund --code 110011                               # Fund details
```

### Information

```bash
groundapi search "AI Agent"                                # Web search
groundapi search "AI Agent" --count 20 --recency oneWeek   # With filters
groundapi scrape https://example.com                       # Scrape webpage
groundapi news                                             # Finance news
groundapi news --category tech --limit 10                  # Tech news
```

### Life Services

```bash
groundapi weather --city 北京                               # Current weather
groundapi weather --city 北京 --forecast                    # 7-day forecast
groundapi weather --location 39.9,116.4                    # By coordinates
groundapi logistics SF1234567890                           # Track package
groundapi ip 8.8.8.8                                       # IP lookup
```

---

## Agent Skills

Pre-built skills that combine GroundAPI tools into automated workflows. Install in Cursor, OpenClaw, or Smithery:

| Skill | Description |
|-------|-------------|
| [Market Briefing](skills/groundapi-market-briefing) | Generates daily A-share market summary — indices, sectors, hot stocks, anomalies |
| [A-Share Analyst](skills/groundapi-a-share-analyst) | Deep analysis with 13 data dimensions — outputs structured report with technicals, financials, capital flow |
| [Stock Screener](skills/groundapi-stock-screener) | Natural language stock screening — "find undervalued bank stocks with high dividends" |
| [Web Researcher](skills/groundapi-web-researcher) | Multi-source research — searches, scrapes, and synthesizes information |
| [Context Aware](skills/groundapi-context-aware) | Location-aware daily assistant — weather, calendar, traffic, news in one shot |
| [Anomaly Tracker](skills/groundapi-anomaly-tracker) | Market anomaly detection — unusual volume, price gaps, limit-up streaks |

---

## Self-hosted MCP Server

Run the MCP server locally (stdio transport for local AI clients):

```bash
pip install -r requirements.txt
python mcp_server.py
```

Or connect to the hosted MCP endpoint (no deployment needed):

```
https://mcp.groundapi.net/mcp
```

---

## Pricing

| | Free | Paid |
|---|---|---|
| **Calls** | 500/month | Pay-as-you-go |
| **Rate Limit** | 60/min | 300/min |
| **Payment** | — | Alipay / WeChat Pay / Credit Card |

Get your API key at [groundapi.net](https://groundapi.net).

## Links

- Website: [groundapi.net](https://groundapi.net)
- API Docs: [docs.groundapi.net](https://docs.groundapi.net)
- MCP Endpoint: `https://mcp.groundapi.net/mcp`
- CLI on PyPI: [groundapi-cli](https://pypi.org/project/groundapi-cli/)
- mcp.so: [GroundAPI on mcp.so](https://mcp.so)

## License

MIT — Skills, MCP server wrapper, and documentation only. GroundAPI is a commercial API service.
