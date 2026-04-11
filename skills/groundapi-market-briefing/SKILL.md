---
name: groundapi-market-briefing
description: Generate A-share market briefing with indices, limit-up/down pools, sector rotation, IPO calendar, and anomaly signals — powered by GroundAPI MCP tools.
metadata:
  openclaw:
    requires:
      env: ["GROUNDAPI_KEY"]
    emoji: "📋"
    homepage: "https://groundapi.net"
    primaryEnv: "GROUNDAPI_KEY"
---

# A 股每日市场简报

当用户询问今日行情、市场简报、盘后总结，或类似以下表达时自动触发：
- "今天A股怎么样"、"市场简报"、"盘后总结"
- "今天涨停的有哪些"、"连板股"、"跌停股"
- "哪个板块强"、"板块轮动"
- "最近有什么新股"

## 前置条件

```json
{
  "mcpServers": {
    "groundapi": {
      "url": "https://mcp.groundapi.net/sse",
      "env": { "GROUNDAPI_KEY": "sk_live_xxxxx" }
    }
  }
}
```

## 执行流程

### Step 1 — 市场全景

`finance_market(scope="overview")` 获取：
- 5 大指数实时：上证/深证/创业板/科创50/北证50
- 市场情绪：涨停数/跌停数/封板成功率/最高连板数

### Step 2 — 热点股池

`finance_market(scope="hot", limit=20)` 获取：
- 涨停股池（含连板数、封板时间、行业）
- 跌停股池
- 强势股池（涨幅前列但未涨停）
- 炸板股池（涨停后打开）
- 次新股池

返回自带**连板梯队统计**（首板X家/2板Y家/3板+Z家）。

### Step 3 — 板块排行

`finance_market(scope="sectors")` 获取概念和行业列表。

如果用户关注特定板块，下钻成分股：
`finance_market(scope="sectors", sector="AI")` → AI概念全部成分股

### Step 4 — 异动信号

`finance_market(scope="signals")` 获取：
- 连续涨停股列表
- 当日涨幅超15%的股票

### Step 5 — 涨跌幅榜

`finance_screen(sort_by="change_pct", order="desc", limit=5)` → 涨幅Top5
`finance_screen(sort_by="change_pct", order="asc", limit=5)` → 跌幅Top5

### Step 6 — 新股日历（可选）

`finance_market(scope="ipo", limit=5)` → 近期新股

### Step 7 — 财经要闻

`info_news(category="finance", limit=10)` → 今日财经新闻

### Step 8 — 组装输出

```
## A 股市场简报 — {YYYY-MM-DD}

### 大盘概览
| 指数 | 点位 | 涨跌幅 | 成交额 |
|------|------|--------|--------|
| 上证指数 | X,XXX | +X.XX% | XXXX亿 |
| 深证成指 | XX,XXX | +X.XX% | XXXX亿 |
| 创业板指 | X,XXX | +X.XX% | XXXX亿 |

市场情绪：涨停XX家 / 跌停XX家 / 封板成功率XX% / 最高XX板

### 连板梯队
| 板数 | 数量 | 代表股 |
|------|------|--------|
| 首板 | XX家 | XXX, XXX |
| 2板 | XX家 | XXX |
| 3板+ | XX家 | XXX |

### 热门板块
领涨：XXX概念 (+X.X%)、YYY概念 (+X.X%)
领跌：XXX概念 (-X.X%)

### 涨幅榜
1. XXX（代码）+XX.X%
2. ...

### 跌幅榜
1. XXX（代码）-XX.X%
2. ...

### 异动信号
- XXX 连续X日涨停
- XXX 今日涨幅XX%

### 今日要闻
- 要闻1
- 要闻2

以上内容基于公开数据，不构成投资建议。
```

## 注意事项

- 非交易时段说明数据为最近一个交易日收盘数据
- 不要编造数据，如果某步获取失败则跳过并说明
- 输出语言跟随用户
