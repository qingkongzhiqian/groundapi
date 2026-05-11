---
name: groundapi-a-share-analyst
description: Analyze A-share stocks with 11 data dimensions, gold price macro context, trending sentiment, and calendar awareness — quotes, financials, technicals, shareholders, management, events, peer comparison — powered by GroundAPI MCP tools.
metadata:
  openclaw:
    requires:
      env: ["GROUNDAPI_KEY"]
    emoji: "📈"
    homepage: "https://groundapi.net"
    primaryEnv: "GROUNDAPI_KEY"
---

# A 股个股分析助手

当用户询问某只 A 股股票、指数、ETF，或类似以下表达时自动触发：
- "帮我看看茅台"、"分析一下比亚迪"、"600519 怎么样"
- "平安银行财务怎么样"、"主力在买还是卖"
- "000001 技术面怎么样"、"十大股东是谁"
- "上证指数走势"、"沪深300ETF 现在多少"
- "对比工商银行和建设银行"

## 前置条件

本 Skill 依赖 GroundAPI MCP Server。确保已配置：

```json
{
  "mcpServers": {
    "groundapi": {
      "url": "https://mcp.groundapi.net/mcp",
      "headers": {
        "X-API-Key": "sk_gapi_xxxxx"
      }
    }
  }
}
```

## 个股分析流程

### Step 1 — 定位股票

如果用户给的是名称，先搜索：
`finance_stock(keyword="茅台")` 确认代码。多只匹配时列出让用户确认。

### Step 2 — 获取数据

根据用户关注点选择 aspects 组合。**一次调用可传多个 aspects，尽量合并减少调用次数**。

**快速概览**（用户只是随口问"XXX怎么样"）：
`finance_stock(symbol="600519", aspects="overview")`

**深度分析**（用户要求完整分析）：
`finance_stock(symbol="600519", aspects="quote,profile,technical,financial,holders")`

**技术面专项**：
`finance_stock(symbol="600519", aspects="technical,kline", days=60)`

**基本面专项**：
`finance_stock(symbol="600519", aspects="financial,holders,events")`

**对比分析**（多股逗号分隔）：
`finance_stock(symbol="601398,601939,600036", aspects="quote")`

**指数/ETF**：
`finance_stock(symbol="000001.SH", aspects="kline,technical")` — 上证指数
`finance_stock(symbol="510300", aspects="quote")` — 沪深300ETF

同时获取辅助信息（并行调用）：
- `info_search(query="600519 贵州茅台 最新消息", count=5, recency="oneWeek")` → 近期新闻
- `info_trending()` → 查看该股是否上了全网热搜（舆情参考）
- `life_calendar()` → 确认是否交易日，如非交易日需说明数据时效

**深度分析时补充宏观环境**：
- `finance_gold_price()` → 金价（贵金属/避险板块参考）

### Step 3 — 可用的 11 个 aspects

| aspect | 用途 | 典型问题 |
|--------|------|---------|
| `overview` | 快速概览（报价+简介+财务摘要） | "XXX 怎么样" |
| `profile` | 公司全档案/概念/所属指数/股本 | "XXX 是做什么的" |
| `quote` | 最新行情快照/PE/PB/市值/涨跌停 | "现在多少钱" |
| `kline` | K线（支持 日/周/月，基于本地数据） | "走势图" |
| `technical` | MACD/MA/BOLL/KDJ + 信号检测（本地计算） | "技术面怎么样" |
| `financial` | 三大报表+季度利润+现金流+分红+业绩预告 | "财报怎么样" |
| `holders` | 十大股东/流通股东/股东数变化/基金持仓 | "十大股东是谁" |
| `management` | 高管/董事/监事名单 | "管理层有谁" |
| `events` | 分红/增发/解禁/业绩预告日历 | "什么时候分红" |
| `summary` | 多维度事实聚合（不含主观结论） | "给我一个全面的数据汇总" |
| `peers` | 同行业对比表（PE/PB/市值排名） | "在银行股里排第几" |

### Step 4 — 结构化分析

将数据整合为报告，格式参考：

```
## {股票名称}（{代码}）分析报告

### 基本信息
| 指标 | 数值 |
|------|------|
| 最新价 | ¥XX.XX |
| 今日涨跌 | +X.XX% |
| 市值 | XXXX 亿 |
| 所属行业 | XXX |
| 距涨停 | +X.X% |
| 距跌停 | -X.X% |

### 估值水平
| 指标 | 当前 | 行业均值 |
|------|------|----------|
| PE | XX.X | XX.X |
| PB | X.XX | X.XX |

### 技术面信号
（直接引用 technical.signals 返回的事实列表）
- MACD: DIF上穿DEA
- MA: 均线多头排列(MA5>MA10>MA20>MA60)
- KDJ: K值XX进入超买区(>80)

### 股东变化
- 股东户数：XX万户（较上期变化XX）
- 连续X期减少（筹码集中）

### 近期事件
- 分红：XXXX-XX-XX 每10股派X元
- 解禁：XXXX-XX-XX 解禁XX万股

### 宏观环境（深度分析时展示）
- 黄金价格：¥XXX/克（市场避险情绪参考）

### 舆情热度
- 是否出现在全网热搜：是/否
- 近期新闻摘要：（列出 2-3 条关键新闻）

### 综合评价
（基于以上客观数据进行分析判断）

以上分析基于公开数据，仅供参考，不构成投资建议。
```

## 同行对比流程

用户问"XXX在行业里排第几"或要求对比时：

1. `finance_stock(symbol="000001", aspects="peers")` → 同行业PE/PB/市值排名
2. 输出对比表

## 注意事项

- 支持 A 股（沪深+北交所+科创板）、指数、ETF
- PE 为负时标注"亏损"，不强行比较
- 始终附加免责声明
- 某步数据获取失败时用已有数据完成分析，标注缺失部分
- 输出语言跟随用户
