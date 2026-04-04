---
name: groundapi-stock-screener
description: Smart A-share stock screener — translate natural language investment preferences into filters and return ranked candidates with details. Powered by GroundAPI MCP tools.
metadata:
  openclaw:
    requires:
      env: ["GROUNDAPI_KEY"]
    emoji: "🔍"
    homepage: "https://groundapi.net"
    primaryEnv: "GROUNDAPI_KEY"
---

# 智能选股助手

当用户表达选股需求或类似以下表达时自动触发：
- "帮我找低估值的消费股"、"有哪些高分红的银行股"
- "筛选一下 PE 低于 20 的股票"、"小盘成长股有哪些"
- "今天涨幅最大的是什么"、"跌幅榜前十"
- "哪些股票股息率超过 5%"

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

### Step 1 — 理解用户意图并映射参数

将用户自然语言偏好转化为 `finance_stock_screen()` 的参数：

| 用户表达 | 参数映射 |
|----------|----------|
| "低估值" | `pe_max=15, pb_max=1.5` |
| "高估值成长" | `pe_min=30` |
| "高分红" / "高股息" | `min_dividend_yield=3, sort_by="dividend_yield"` |
| "大盘股" | `min_market_cap=50000000000`（500 亿） |
| "中盘股" | `min_market_cap=10000000000, max_market_cap=50000000000` |
| "小盘股" | `max_market_cap=10000000000`（100 亿） |
| "今天涨最多" | `sort_by="change_pct", order="desc"` |
| "今天跌最多" | `sort_by="change_pct", order="asc"` |
| 行业关键词（"半导体"、"白酒"、"银行"） | `industry="半导体"` |

如果用户给了模糊描述（如"稳健的股票"），合理推断为：低 PE + 高分红 + 大市值，并告诉用户你的推断逻辑。

### Step 2 — 执行筛选

调用 `finance_stock_screen(...)` 获取符合条件的股票列表，默认返回 20 只。

### Step 3 — 补充 Top 候选详情

对排名前 5 的股票，逐一调用：
`finance_stock(symbol="...", include="fundamental")` 获取详细基本面数据。

### Step 4 — 结构化输出

```
## 🔍 选股结果 — {筛选条件摘要}

### 筛选条件
- 行业：XXX
- PE：< XX
- 市值：> XXX 亿
- 排序：按 XXX 降序

### 筛选结果（共 X 只）

| # | 股票 | 代码 | 最新价 | 涨跌幅 | PE | PB | 股息率 | 市值(亿) |
|---|------|------|--------|--------|-----|-----|--------|----------|
| 1 | XXX | XXXXXX | ¥XX.XX | +X.X% | XX.X | X.X | X.X% | XXX |
| ... |

### Top 5 详细点评

**1. XXX（XXXXXX）**
- 估值：PE XX.X（行业均值 XX.X），PB X.X
- 亮点：一句话概述
- 风险：一句话概述

（重复 5 只）

⚠️ 以上筛选基于公开数据，仅供参考，不构成投资建议。
```

## 追问交互

如果用户对结果不满意，支持追问调整：
- "PE 再低一点" → 收紧 pe_max
- "换个行业看看" → 修改 industry
- "按市值排序" → 修改 sort_by
- "详细看看第三个" → 对该股票触发个股分析流程

## 注意事项

- 仅支持 A 股（沪深两市）
- 筛选条件过于严格导致无结果时，建议用户放宽条件并说明哪个条件最受限
- 始终附加免责声明
- 输出语言跟随用户
