# REST Connector YAML 映射

真实工厂里的 MES API 通常已经定型，字段名、URL 和返回结构不会为了 Agent 改造。
ManuGent 的 REST connector 通过 YAML 映射把标准 MES tools 适配到企业现有接口。

## 配置方式

```bash
MES_TYPE=rest
MES_BASE_URL=https://mes.example.com
MES_API_TOKEN=your-token
MES_MAPPING_PATH=configs/rest-mapping.example.yaml
```

不配置 `MES_MAPPING_PATH` 时，系统会使用内置默认映射。

## YAML 结构

```yaml
tools:
  query_production_data:
    method: GET
    path: /api/v1/production/metrics
    param_map:
      line_id: lineCode
      metric: metric
      time_range: range
      granularity: bucket
    response_path: result.data
```

字段说明：

- `method`：当前支持 `GET` 和 `POST`。
- `path`：MES API 路径，支持 `{equipment_id}` 这类路径参数。
- `param_map`：把 ManuGent tool 参数映射为企业 MES API 参数。
- `response_path`：从嵌套 JSON 中提取业务数据，例如 `result.data`。

## 设计原则

- Agent 仍然只看到标准 tools，不直接感知各厂商 MES API 差异。
- 同一套 workflow 可以接入不同 MES，只需要替换 YAML 映射。
- YAML 只做接口适配，不承载业务推理，避免把根因分析逻辑散落到配置文件里。
