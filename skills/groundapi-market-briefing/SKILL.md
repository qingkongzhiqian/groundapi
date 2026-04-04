---
name: groundapi-market-briefing
description: Generate a daily A-share market briefing covering indices, sector rotation, top movers, and key financial news — powered by GroundAPI MCP tools.
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
- "今天涨了还是跌了"、"大盘表现如何"
- "daily briefing"、"market summary"

## 前置条件

本 Skill 依赖 GroundAPI MCP Server 提供的工具。确保已配置 GroundAPI MCP 连接：

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

按以下顺序调用 GroundAPI 工具，收集完整数据后再统一输出：

### Step 1 — 市场全景

调用 `finance_market(include="sectors,funds,valuation,macro")` 获取：
- 主要指数（上证、深证、创业板）涨跌幅与成交量
- 市场涨跌家数（breadth）
- 板块涨跌排行
- 基金净值变动排行
- 主要宏观指标

### Step 2 — 涨跌幅榜

并行调用两次 `finance_stock_screen`：
- `finance_stock_screen(sort_by="change_pct", order="desc", limit=5)` → 涨幅 Top 5
- `finance_stock_screen(sort_by="change_pct", order="asc", limit=5)` → 跌幅 Top 5

### Step 3 — 财经要闻

调用 `info_news(category="finance", limit=10)` 获取今日重要财经新闻。

### Step 4 — 组装输出

将以上数据整合为以下格式：

```
## 📋 A 股市场简报 — {YYYY-MM-DD}

### 大盘概览
| 指数 | 点位 | 涨跌幅 | 成交额 |
|------|------|--------|--------|
（上证、深证、创业板数据）

上涨 X 家 / 下跌 Y 家 / 平盘 Z 家

### 板块轮动
🔴 领涨：XXX (+X.X%), YYY (+X.X%), ZZZ (+X.X%)
🟢 领跌：XXX (-X.X%), YYY (-X.X%), ZZZ (-X.X%)

### 个股风云
📈 涨幅榜：
1. XXX（代码）+X.X% — 一句话点评
...

📉 跌幅榜：
1. XXX（代码）-X.X% — 一句话点评
...

### 今日要闻
- 要闻1（来源）
- 要闻2（来源）
- 要闻3（来源）

### 明日关注
（基于今日板块轮动和新闻，给出 2-3 条明日关注点）
```

## 注意事项

- 非交易时段（工作日 15:00 之后、周末、节假日）说明数据为最近一个交易日的收盘数据
- "明日关注"仅为基于公开数据的观察提示，始终附加"以上内容不构成投资建议"
- 如果某一步数据获取失败，跳过该部分并告知用户，不要编造数据
- 输出语言跟随用户：用户用中文提问则中文输出，英文提问则英文输出
