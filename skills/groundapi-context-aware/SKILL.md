---
name: groundapi-context-aware
description: Context-aware daily assistant — auto-detect user location via IP, provide local weather, track packages, and offer lifestyle tips. Powered by GroundAPI MCP tools.
metadata:
  openclaw:
    requires:
      env: ["GROUNDAPI_KEY"]
    emoji: "🌤️"
    homepage: "https://groundapi.net"
    primaryEnv: "GROUNDAPI_KEY"
---

# 情境感知生活助手

当用户进行日常问候、询问天气、查快递、查 IP，或类似以下表达时自动触发：
- "今天天气怎么样"、"需要带伞吗"、"这周天气如何"
- "我的快递到哪了"、"帮我查一下运单号 XXX"
- "我现在在哪"、"帮我查一下这个 IP"
- "早上好"、"今天穿什么合适"

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

## 场景一：天气查询

### 用户指定了城市

直接调用 `life_weather(city="北京", forecast=true)` 获取实时天气 + 7 天预报。

### 用户没指定城市

1. 调用 `life_ip()` 获取用户大致位置（城市）
2. 用返回的城市调用 `life_weather(city="...", forecast=true)`

### 输出格式

```
## 🌤️ {城市} 天气

### 当前
- 天气：{天气状况}
- 温度：{当前温度}°C（体感 {体感温度}°C）
- 湿度：{湿度}% | 风：{风向} {风力}
- 能见度：{能见度}

### 未来 7 天
| 日期 | 天气 | 最高 | 最低 | 建议 |
|------|------|------|------|------|
| 周一 | ☀️ 晴 | 28°C | 15°C | 适合户外 |
| ... |

### 生活建议
- 穿衣：{根据温度和天气给出建议}
- 出行：{是否需要带伞/防晒等}
```

## 场景二：快递追踪

当用户提供运单号时：

1. 调用 `life_logistics(number="SF1234567890")` 追踪物流
2. 如果是顺丰快递且需要验证，提示用户提供收件人手机后四位

### 输出格式

```
## 📦 快递追踪

- 运单号：{number}
- 快递公司：{company}
- 当前状态：{status}

### 物流轨迹
| 时间 | 状态 |
|------|------|
| 04-03 14:30 | 已签收 |
| 04-03 08:15 | 派送中 |
| 04-02 22:00 | 到达 XX 营业部 |
| ... |

预计 {到达时间判断，如果已签收则不显示}
```

## 场景三：IP 地理定位

当用户提到查 IP 或给出一个 IP 地址时：

调用 `life_ip(address="8.8.8.8")` 或 `life_ip()`（查自己）。

### 输出格式

```
## 📍 IP 定位：{IP 地址}

| 信息 | 值 |
|------|-----|
| 国家/地区 | {country} |
| 城市 | {city} |
| 经纬度 | {lat}, {lon} |
| 时区 | {timezone} |
| ISP | {isp} |
```

## 场景四：日常问候（组合技）

当用户说"早上好"、"今天怎么样"等日常问候时，自动组合多个工具：

1. `life_ip()` → 定位城市
2. `life_weather(city="...", forecast=false)` → 当前天气
3. `info_news(category="general", limit=3)` → 今日要闻

输出一段自然的问候回复，包含当地天气和今日要闻摘要，语气轻松友好。

## 注意事项

- IP 定位精度有限（通常到城市级别），不要声称是精确位置
- 天气数据来自和风天气，支持中英文城市名
- 快递公司通常可自动识别，无需用户指定
- 顺丰快递比较特殊，需要收件人手机后四位验证
- 输出语言跟随用户
