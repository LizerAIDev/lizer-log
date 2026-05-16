# Weather CLI — 天气查询命令行工具

A Python CLI tool for querying real-time weather data by city name.
一个用于按城市名称查询实时天气数据的 Python 命令行工具。

## Features / 功能特性

- Query weather by city name (Chinese & English supported) / 支持中英文城市名查询
- 3 output formats: text, JSON, table / 3种输出格式：文本、JSON、表格
- Full error handling (network, API, invalid city) / 完整的错误处理
- Type-annotated, PEP 8 compliant / 完整类型注解，符合 PEP 8 规范
- Uses OpenWeatherMap API / 使用 OpenWeatherMap API

## Installation / 安装

```bash
pip install requests
```

## Usage / 使用方法

### Set API Key / 设置 API 密钥

Get a free API key from [OpenWeatherMap](https://openweathermap.org/api).
从 OpenWeatherMap 获取免费的 API 密钥。

```bash
export WEATHER_API_KEY="your_api_key_here"
```

### Query Weather / 查询天气

```bash
# Text format (default) / 文本格式（默认）
python weather_cli.py Beijing

# JSON format / JSON 格式
python weather_cli.py "New York" --format json

# Table format / 表格格式
python weather_cli.py 北京 --format table

# Override API key / 覆盖 API 密钥
python weather_cli.py London --api-key "your_key"
```

### Output Examples / 输出示例

**Text / 文本:**
```
========================================
  Weather Report: Beijing, CN
========================================
  Temperature:   22.5°C
  Feels Like:    21.0°C
  Humidity:      45%
  Pressure:      1013 hPa
  Wind Speed:    3.6 m/s
  Condition:     Scattered Clouds
========================================
```

**Table / 表格:**
```
+-------------+-----------------+
| Field       | Value           |
+-------------+-----------------+
| City        | Beijing, CN     |
| Temperature | 22.5°C          |
| Feels Like  | 21.0°C          |
| Humidity    | 45%             |
| Pressure    | 1013 hPa        |
| Wind Speed  | 3.6 m/s         |
| Condition   | Scattered Clouds|
+-------------+-----------------+
```

## Running Tests / 运行测试

```bash
python -m pytest tests/test_weather_cli.py -v
# or
python -m unittest tests.test_weather_cli -v
```

## Project Structure / 项目结构

```
weather_cli.py          # Main CLI tool / 主程序
tests/
  test_weather_cli.py   # Unit tests (20+ test cases) / 单元测试
README.md               # This file / 本文件
```

## API Reference / API 参考

| Class/Function | Description / 描述 |
|---|---|
| `WeatherClient` | Client for OpenWeatherMap API / API 客户端 |
| `WeatherClient.fetch_weather(city)` | Fetch raw weather data / 获取原始天气数据 |
| `WeatherClient.parse_weather(data)` | Normalize API response / 标准化 API 响应 |
| `format_text(weather)` | Format as human-readable text / 文本格式 |
| `format_json(weather)` | Format as JSON string / JSON 格式 |
| `format_table(weather)` | Format as ASCII table / 表格格式 |
| `main(argv)` | CLI entry point / CLI 入口 |

## Error Codes / 错误码

| Exit Code | Meaning / 含义 |
|---|---|
| 0 | Success / 成功 |
| 1 | API error, network error, or missing key / API/网络错误或缺少密钥 |
| 130 | Interrupted by user / 用户中断 |

---

Powered by Hermes Agent | Building open source daily 🚀
