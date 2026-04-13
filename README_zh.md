<p align="center">
  <h1 align="center">GroundAPI</h1>
  <p align="center"><strong>面向 AI Agent 的实时数据 API</strong></p>
  <p align="center">
    <a href="https://groundapi.net">官网</a> · <a href="https://docs.groundapi.net">文档</a> · <a href="https://mcp.groundapi.net/mcp">MCP 端点</a> · <a href="https://pypi.org/project/groundapi-cli/">CLI</a>
  </p>
  <p align="center">
    中文 | <a href="./README.md">English</a>
  </p>
</p>

---

GroundAPI 为 AI Agent 提供一站式实时数据层 — **18 个工具**，覆盖金融、信息、生活三大类别。一个 API Key，三种接入方式：**REST API**、**MCP**、**CLI**。

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://mcp.groundapi.net/mcp)
[![PyPI](https://img.shields.io/pypi/v/groundapi-cli.svg)](https://pypi.org/project/groundapi-cli/)

## 目录

- [快速开始](#快速开始)
- [MCP 工具详解](#mcp-工具详解)
  - [金融数据（6 个工具）](#金融数据6-个工具)
  - [信息检索（5 个工具）](#信息检索5-个工具)
  - [生活服务（7 个工具）](#生活服务7-个工具)
- [REST API](#rest-api)
- [CLI 命令参考](#cli-命令参考)
- [Agent Skills](#agent-skills)
- [自托管 MCP Server](#自托管-mcp-server)
- [定价](#定价)

## 快速开始

前往 [groundapi.net](https://groundapi.net) 注册 — **每月 500 次免费调用**，无需信用卡。

### 方式一：MCP 接入（推荐 AI Agent 使用）

在 Claude Desktop、Cursor、Windsurf 或任意 MCP 兼容客户端中添加：

```json
{
  "mcpServers": {
    "groundapi": {
      "url": "https://mcp.groundapi.net/mcp",
      "headers": {
        "X-API-Key": "你的_API_KEY"
      }
    }
  }
}
```

### 方式二：REST API

```bash
curl -H "X-API-Key: 你的_API_KEY" \
  "https://api.groundapi.net/v1/finance/stock?symbol=600519&aspects=overview"
```

### 方式三：CLI 命令行

```bash
pip install groundapi-cli
groundapi config set-key 你的_API_KEY
groundapi stock --symbol 600519
```

---

## MCP 工具详解

### 金融数据（6 个工具）

#### `finance_stock` — 证券数据一站式查询

支持个股、指数、ETF，**13 个数据维度**，支持多股对比。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `symbol` | string | — | 股票代码，逗号分隔可对比（如 `"600519,000858"`） |
| `keyword` | string | — | 按名称搜索（如 `"茅台"`） |
| `aspects` | string | `"overview"` | 数据维度，逗号分隔（见下表） |
| `days` | int | `60` | K线/技术面历史天数 |
| `period` | string | `"d"` | K线周期：`5/15/30/60/d/w/m` |

**13 个数据维度：**

| 维度 | 返回内容 | 适用场景 |
|------|----------|----------|
| `overview` | 快速概览：报价 + 简介 + 财务摘要 | "XXX 怎么样" |
| `profile` | 公司全档案、概念、所属指数、股本结构 | "这公司是做什么的" |
| `quote` | 实时价格、PE/PB、五档盘口、距涨跌停距离 | "现在多少钱" |
| `kline` | K线数据（支持 5/15/30/60 分钟、日/周/月线） | "走势怎么样" |
| `technical` | MACD/MA/BOLL/KDJ + 信号检测（如"DIF上穿DEA"） | "技术面怎么样" |
| `financial` | 三大报表、季度利润、现金流、分红、业绩预告 | "财报怎么样" |
| `flow` | 资金流向（超大/大/中/小单）、连续净流入/出天数 | "主力在买还是卖" |
| `holders` | 十大股东、流通股东、股东数趋势、基金持仓 | "十大股东是谁" |
| `management` | 高管、董事、监事名单 | "管理层有谁" |
| `events` | 分红、增发、解禁、业绩预告日历 | "什么时候分红" |
| `tick` | 当天逐笔交易（买卖方向统计） | "今天买盘多还是卖盘多" |
| `summary` | 多维度事实聚合（不含主观结论） | "给我一个全面的数据汇总" |
| `peers` | 同行业对比表（PE/PB/市值排名） | "在银行股里排第几" |

```python
# 快速概览
finance_stock(symbol="600519")

# 多维度深度分析
finance_stock(symbol="600519", aspects="quote,technical,financial,flow")

# 按名称搜索
finance_stock(keyword="平安")

# 多股对比
finance_stock(symbol="601398,601939,600036", aspects="quote")

# 指数 / ETF
finance_stock(symbol="000001.SH", aspects="kline,technical")  # 上证指数
finance_stock(symbol="510300", aspects="quote")                # 沪深300ETF
```

#### `finance_market` — 市场全景

大盘指数、涨跌停股池、板块排名、新股日历、异动信号。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `scope` | string | `"overview"` | 数据范围，逗号分隔 |
| `sector` | string | — | 下钻到具体板块 |
| `date` | string | — | 日期筛选（YYYY-MM-DD） |

**Scope 选项：** `overview`（指数 + 情绪）· `hot`（涨跌停股池、连板梯队）· `sectors`（概念/行业列表）· `ipo`（新股日历）· `signals`（异动信号）

```python
finance_market()                                    # 今日大盘
finance_market(scope="hot")                         # 涨跌停股
finance_market(scope="sectors", sector="AI")        # AI板块成分股
finance_market(scope="ipo")                         # 新股日历
```

#### `finance_screen` — 智能选股

多条件筛选，20+ 维度，内置预设组合。

| 参数 | 类型 | 说明 |
|------|------|------|
| `industry` | string | 行业（如 `"银行"`、`"半导体"`） |
| `concept` | string | 概念（如 `"AI"`、`"新能源"`） |
| `pe_max` / `pe_min` | float | PE 区间 |
| `pb_max` | float | 最大 PB |
| `min_market_cap` / `max_market_cap` | float | 市值区间 |
| `min_dividend_yield` | float | 最低股息率（%） |
| `filter_preset` | string | `low_pe_high_div` · `small_cap_growth` · `large_cap_stable` |
| `sort_by` | string | 排序字段（默认 `change_pct`） |

```python
finance_screen(industry="银行", pe_max=10)                       # 低估值银行股
finance_screen(min_dividend_yield=3, sort_by="dividend_yield")   # 高分红
finance_screen(concept="AI")                                      # AI概念股
finance_screen(filter_preset="low_pe_high_div")                  # 预设：价值型
```

#### `finance_search` — 全市场搜索

覆盖 **11,780+ 条目**：股票、概念、行业、ETF、指数。

| 参数 | 类型 | 说明 |
|------|------|------|
| `keyword` | string | 搜索关键词 |
| `type` | string | `all` · `stock`（6,104）· `concept`（2,222）· `sector`（1,466）· `etf`（1,377）· `index`（613） |

```python
finance_search(keyword="芯片", type="etf")        # 芯片ETF
finance_search(keyword="AI", type="concept")       # AI概念指数
finance_search(keyword="沪深300", type="index")    # 沪深300
```

#### `finance_exchange_rate` — 汇率查询

```python
finance_exchange_rate(from_currency="USD", to_currency="CNY")
finance_exchange_rate(from_currency="EUR", to_currency="JPY")
```

#### `finance_gold_price` — 贵金属价格

```python
finance_gold_price()   # 黄金、白银、铂金实时价格
```

---

### 信息检索（5 个工具）

#### `info_search` — 网络搜索

| 参数 | 类型 | 说明 |
|------|------|------|
| `query` | string | 搜索关键词 |
| `count` | int | 结果数量（1–50，默认 10） |
| `recency` | string | `noLimit` · `oneDay` · `oneWeek` · `oneMonth` · `oneYear` |

```python
info_search(query="最新AI政策", count=20, recency="oneWeek")
```

#### `info_scrape` — 网页抓取

```python
info_scrape(url="https://example.com")   # 返回 Markdown 格式内容
```

#### `info_news` — 新闻头条

| 参数 | 类型 | 说明 |
|------|------|------|
| `category` | string | `finance` · `general` · `tech` · `sports` ... |
| `limit` | int | 文章数量（1–50） |

```python
info_news(category="finance", limit=10)
info_news(category="tech")
```

#### `info_trending` — 全网热搜

微博、抖音、知乎等平台实时热搜榜。

```python
info_trending()
```

#### `info_bulletin` — 每日简报

```python
info_bulletin()   # 每日新闻摘要
```

---

### 生活服务（7 个工具）

#### `life_weather` — 天气查询

| 参数 | 类型 | 说明 |
|------|------|------|
| `city` | string | 城市名（如 `"北京"`） |
| `location` | string | 经纬度（如 `"39.9,116.4"`） |
| `forecast` | bool | 是否包含 7 日预报 |

```python
life_weather(city="北京", forecast=True)
life_weather(location="39.9,116.4")
```

#### `life_logistics` — 快递追踪

```python
life_logistics(number="SF1234567890")              # 自动识别快递公司
life_logistics(number="1234567890", company="yt")   # 指定快递公司
```

#### `life_ip` — IP 地理定位

```python
life_ip(address="8.8.8.8")   # 国家、城市、时区、运营商
life_ip()                     # 查询本机 IP
```

#### `life_tax` — 个人所得税计算器

```python
life_tax(monthly_salary=20000, insurance=2000, special_deduction=1500)
```

#### `life_calendar` — 万年历

```python
life_calendar()                  # 今天：农历、节气、节假日、是否交易日
life_calendar(date="2026-05-01") # 查询指定日期
```

#### `life_oil_price` — 油价查询

```python
life_oil_price()                  # 全国均价
life_oil_price(province="北京")   # 指定省份
```

#### `life_traffic` — 限行查询

```python
life_traffic(city="北京")   # 今日限行尾号
```

---

## REST API

Base URL：`https://api.groundapi.net`

所有请求需要 `X-API-Key` 请求头。

| 端点 | 说明 |
|------|------|
| `GET /v1/finance/stock` | 股票/指数/ETF 数据 |
| `GET /v1/finance/market` | 市场全景 |
| `GET /v1/finance/stock/screen` | 股票筛选 |
| `GET /v1/finance/search` | 证券搜索 |
| `GET /v1/finance/exchange-rate` | 汇率 |
| `GET /v1/finance/gold-price` | 贵金属价格 |
| `GET /v1/info/search` | 网络搜索 |
| `GET /v1/info/scrape` | 网页抓取 |
| `GET /v1/info/news` | 新闻 |
| `GET /v1/info/trending` | 热搜 |
| `GET /v1/info/bulletin` | 每日简报 |
| `GET /v1/life/weather` | 天气 |
| `GET /v1/life/logistics` | 快递追踪 |
| `GET /v1/life/ip` | IP 定位 |
| `GET /v1/life/tax` | 个税计算 |
| `GET /v1/life/calendar` | 万年历 |
| `GET /v1/life/oil-price` | 油价 |
| `GET /v1/life/traffic` | 限行 |

```bash
# 个股概览
curl -H "X-API-Key: 你的KEY" \
  "https://api.groundapi.net/v1/finance/stock?symbol=600519&aspects=overview"

# 多维度深度分析
curl -H "X-API-Key: 你的KEY" \
  "https://api.groundapi.net/v1/finance/stock?symbol=600519&aspects=quote,technical,financial"

# 大盘总览
curl -H "X-API-Key: 你的KEY" \
  "https://api.groundapi.net/v1/finance/market?scope=overview"

# 条件选股
curl -H "X-API-Key: 你的KEY" \
  "https://api.groundapi.net/v1/finance/stock/screen?industry=银行&pe_max=10"

# 网络搜索
curl -H "X-API-Key: 你的KEY" \
  "https://api.groundapi.net/v1/info/search?q=AI+Agent&count=10"

# 天气查询
curl -H "X-API-Key: 你的KEY" \
  "https://api.groundapi.net/v1/life/weather?city=北京&forecast=true"
```

完整 API 文档：[docs.groundapi.net](https://docs.groundapi.net)

---

## CLI 命令参考

### 安装

```bash
pip install groundapi-cli
groundapi config set-key 你的_API_KEY
```

### 金融

```bash
# A 股行情
groundapi stock --symbol 600519                            # 实时行情
groundapi stock --keyword 贵州茅台                          # 搜索股票
groundapi stock --symbol 600519 --date 2024-12-31          # 指定日期日K
groundapi stock --symbol 600519 --days 30                  # 最近30天历史
groundapi stock --symbol 600519 --days 30 --include technicals  # 历史+技术指标

# 股票筛选
groundapi screen                                           # 默认排行（涨跌幅）
groundapi screen --industry 白酒 --pe-max 30               # 行业+PE筛选
groundapi screen --sort-by total_market_cap --limit 10     # 市值前10

# 大盘总览
groundapi market                                           # 大盘+宏观
groundapi market --include sectors,valuation               # 板块+估值
groundapi market --sector 半导体 --type industry           # 板块详情

# 基金
groundapi fund                                             # 基金排行
groundapi fund --keyword 沪深300                            # 搜索基金
groundapi fund --code 110011                               # 基金详情
```

### 资讯

```bash
groundapi search "AI Agent"                                # 网络搜索
groundapi search "AI Agent" --count 20 --recency oneWeek   # 限定时间
groundapi scrape https://example.com                       # 网页抓取
groundapi news                                             # 财经新闻
groundapi news --category tech --limit 10                  # 科技新闻
```

### 生活

```bash
groundapi weather --city 北京                               # 实时天气
groundapi weather --city 北京 --forecast                    # 7天预报
groundapi weather --location 39.9,116.4                    # 经纬度查询
groundapi logistics SF1234567890                           # 快递追踪
groundapi ip 8.8.8.8                                       # IP 定位
```

---

## Agent Skills

预构建技能，将 GroundAPI 工具组合为自动化工作流。可在 Cursor、OpenClaw 或 Smithery 中安装：

| 技能 | 说明 |
|------|------|
| [Market Briefing](skills/groundapi-market-briefing) | 每日 A 股市场速报 — 指数、板块、热股、异动一网打尽 |
| [A-Share Analyst](skills/groundapi-a-share-analyst) | 13 维度个股深度分析 — 输出结构化研报，含技术面、财务、资金流 |
| [Stock Screener](skills/groundapi-stock-screener) | 自然语言选股 — "找低估值高分红的银行股" |
| [Web Researcher](skills/groundapi-web-researcher) | 多源深度调研 — 搜索、抓取、综合分析一条龙 |
| [Context Aware](skills/groundapi-context-aware) | 场景感知生活助手 — 天气、日历、限行、新闻一站查 |
| [Anomaly Tracker](skills/groundapi-anomaly-tracker) | 市场异动监测 — 异常放量、跳空缺口、连板追踪 |

---

## 自托管 MCP Server

通过 stdio 传输在本地运行（适合本地 AI 客户端）：

```bash
pip install -r requirements.txt
python mcp_server.py
```

或直接使用托管 MCP 端点（无需部署）：

```
https://mcp.groundapi.net/mcp
```

---

## 定价

| | 免费版 | 付费版 |
|---|---|---|
| **调用次数** | 500 次/月 | 按量计费 |
| **频率限制** | 60 次/分钟 | 300 次/分钟 |
| **支付方式** | — | 支付宝 / 微信支付 / 信用卡 |

前往 [groundapi.net](https://groundapi.net) 注册获取 API Key。

## 链接

- 官网：[groundapi.net](https://groundapi.net)
- API 文档：[docs.groundapi.net](https://docs.groundapi.net)
- MCP 端点：`https://mcp.groundapi.net/mcp`
- CLI (PyPI)：[groundapi-cli](https://pypi.org/project/groundapi-cli/)
- mcp.so：[GroundAPI on mcp.so](https://mcp.so)

## 许可证

MIT — 仅限 Skills、MCP Server 封装和文档。GroundAPI 是商业 API 服务。
