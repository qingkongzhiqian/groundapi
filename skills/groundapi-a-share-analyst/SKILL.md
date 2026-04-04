---
name: groundapi-a-share-analyst
description: Analyze individual A-share stocks with real-time quotes, fundamentals, technicals, and recent news — powered by GroundAPI MCP tools.
metadata:
  openclaw:
    requires:
      env: ["GROUNDAPI_KEY"]
    emoji: "📈"
    homepage: "https://groundapi.net"
    primaryEnv: "GROUNDAPI_KEY"
---

# A 股个股分析助手

当用户询问某只 A 股股票、某个行业板块，或类似以下表达时自动触发：
- "帮我看看茅台"、"分析一下比亚迪"、"600519 怎么样"
- "半导体板块最近表现如何"
- "宁德时代值得买吗"、"这只股票估值高不高"

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

## 个股分析流程

当用户提到具体股票名称或代码时，按以下步骤执行：

### Step 1 — 定位股票

如果用户给的是名称而非代码，先调用：
`finance_stock(keyword="茅台")` 搜索匹配，确认股票代码。

如果匹配到多只股票，列出让用户确认。

### Step 2 — 获取数据（尽量并行调用）

同时发起以下请求：
- `finance_stock(symbol="600519", include="fundamental")` → 基本面数据（PE、PB、股息率、市值、ROE 等）
- `finance_stock(symbol="600519", days=60, include="technicals", indicators="ma,macd,rsi,kdj,boll")` → 近 60 个交易日行情 + 技术指标
- `info_search(query="600519 贵州茅台 最新消息", count=5, recency="oneWeek")` → 近一周相关新闻

### Step 3 — 结构化分析

将数据整合为以下报告格式：

```
## 📈 {股票名称}（{代码}）分析报告

### 基本信息
| 指标 | 数值 |
|------|------|
| 最新价 | ¥X,XXX.XX |
| 今日涨跌 | +X.XX% |
| 市值 | XXXX 亿 |
| 所属行业 | XXX |

### 估值水平
| 指标 | 数值 | 行业均值 | 判断 |
|------|------|----------|------|
| PE (TTM) | XX.X | XX.X | 偏高/合理/偏低 |
| PB | X.XX | X.XX | 偏高/合理/偏低 |
| 股息率 | X.XX% | X.XX% | — |

### 技术面信号
- **趋势**：MA5/MA20/MA60 排列状态 → 多头/空头/震荡
- **MACD**：DIF 与 DEA 关系 → 金叉/死叉/背离
- **RSI**：当前值 → 超买(>70)/中性/超卖(<30)
- **综合判断**：一句话技术面总结

### 近期催化剂
- 新闻1（来源，日期）
- 新闻2（来源，日期）
- 新闻3（来源，日期）

### 综合评价
（2-3 句话，结合基本面、技术面、近期消息的综合判断）

⚠️ 以上分析基于公开数据，仅供参考，不构成投资建议。
```

## 行业板块分析流程

当用户提到行业或板块（如"半导体"、"新能源"、"银行板块"）时：

### Step 1 — 板块概览
调用 `finance_market(sector="半导体")` 获取板块数据和成分股。

### Step 2 — 板块内排名
调用 `finance_stock_screen(industry="半导体", sort_by="change_pct", limit=10)` 获取板块内今日涨跌排名。

### Step 3 — 估值对比
调用 `finance_market(include="valuation")` 获取该行业的估值在全市场中的位置。

### Step 4 — 输出板块分析
```
## 🏭 {板块名称} 板块分析

### 板块表现
今日涨跌幅：+X.XX%（全市场排名 X/N）
近5日累计：+X.XX%

### 板块内 Top 10
| 排名 | 股票 | 涨跌幅 | 市值 | PE |
|------|------|--------|------|-----|
（表格数据）

### 板块估值
当前 PE 中位数：XX.X（历史分位 XX%）

### 板块点评
（2-3 句基于数据的客观分析）
```

## 注意事项

- 仅支持 A 股（沪深两市），用户问港股/美股时告知不在覆盖范围
- PE 为负或极端值时标注"亏损"或"不适用"，不要强行比较
- 始终附加免责声明
- 如果某一步数据获取失败，用已有数据完成分析，标注哪部分数据缺失
- 输出语言跟随用户
