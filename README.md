# GroundAPI

**Real-time Data API for AI Agents**

GroundAPI provides a unified data layer for AI Agents — 10 tools covering A-share finance, web search, news, weather, logistics, and more. Supports REST API, MCP, and CLI.

🌐 [Website](https://groundapi.net) · 📖 [Documentation](https://docs.groundapi.net) · 🔌 [MCP Server](https://mcp.groundapi.net)

---

## Features

### Finance (4 tools)
- **Stock Data** — Real-time A-share quotes, fundamentals, technicals, historical data
- **Stock Screener** — Multi-criteria screening with 20+ dimensions
- **Market Overview** — Indices, sector rotation, breadth, macro indicators
- **Fund Data** — Fund search, ranking, NAV, and manager info

### Information (3 tools)
- **Web Search** — Multi-engine web search with recency filters
- **Web Scraper** — Extract clean markdown from any webpage
- **News** — Latest headlines by category (finance, tech, general, etc.)

### Life Services (3 tools)
- **Weather** — Current conditions + 7-day forecast for any city
- **Logistics** — Track packages across major courier companies
- **IP Geolocation** — Country, city, timezone, ISP lookup

## Quick Start

### MCP (for AI Agents)

Add to your Claude Desktop, Cursor, Windsurf, or any MCP-compatible client:

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

### REST API

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
  "https://api.groundapi.net/v1/life/weather?city=Beijing"
```

### CLI

```bash
pip install groundapi-cli
groundapi config set-key YOUR_API_KEY
groundapi stock 600519
groundapi weather Beijing
```

## MCP Tools Reference

| Tool | Description | Example |
|------|-------------|---------|
| `finance_stock` | Query A-share stock data | `finance_stock(symbol="600519")` |
| `finance_stock_screen` | Screen stocks by criteria | `finance_stock_screen(industry="半导体", pe_max=30)` |
| `finance_market` | Get market overview & sectors | `finance_market(include="sectors,macro")` |
| `finance_fund` | Query fund data | `finance_fund(keyword="沪深300")` |
| `info_search` | Search the web | `info_search(query="AI trends 2026")` |
| `info_scrape` | Read a webpage as markdown | `info_scrape(url="https://example.com")` |
| `info_news` | Get latest news | `info_news(category="finance")` |
| `life_weather` | Get weather data | `life_weather(city="Tokyo", forecast=true)` |
| `life_logistics` | Track a package | `life_logistics(number="SF1234567890")` |
| `life_ip` | IP geolocation | `life_ip(address="8.8.8.8")` |

## Pricing

- **Free Tier**: 500 calls/month
- **Rate Limits**: Free 60/min, Paid 300/min
- **Payment**: Alipay / WeChat Pay / Credit Card

Get your API key at [groundapi.net](https://groundapi.net).

## Agent Skills

Pre-built skills for OpenClaw and Smithery that combine GroundAPI tools into ready-to-use workflows:

| Skill | Description |
|-------|-------------|
| [Market Briefing](skills/groundapi-market-briefing/) | Daily A-share market summary |
| [A-Share Analyst](skills/groundapi-a-share-analyst/) | Individual stock analysis |
| [Stock Screener](skills/groundapi-stock-screener/) | Smart stock screening |
| [Web Researcher](skills/groundapi-web-researcher/) | Deep web research & synthesis |
| [Context Aware](skills/groundapi-context-aware/) | Location-aware daily assistant |

## Links

- Website: [groundapi.net](https://groundapi.net)
- API Docs: [docs.groundapi.net](https://docs.groundapi.net)
- MCP Server: [mcp.groundapi.net](https://mcp.groundapi.net)
- Smithery: [smithery.ai](https://smithery.ai/server/qingkongzhiqian/ground-api)
- CLI on PyPI: [groundapi-cli](https://pypi.org/project/groundapi-cli/)

## License

MIT — Skills and documentation only. GroundAPI is a commercial API service.
