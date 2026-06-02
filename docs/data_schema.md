# Data Schema

## 1. Export Manifest

`scan-export-root` 输出的 manifest 结构：

```json
{
  "scanned_at": "2026-06-02T12:00:00+08:00",
  "export_root": "C:/path/to/export_root",
  "private_contact_count": 2,
  "group_count": 1,
  "records": [
    {
      "bucket": "private",
      "source_name": "someone",
      "relative_path": "contacts/someone.json",
      "file_size_bytes": 48123,
      "message_count": 730
    }
  ]
}
```

## 2. Redacted Manifest

`redact-manifest` 会把真实标识替换成公开安全字段：

```json
{
  "records": [
    {
      "bucket": "private",
      "public_contact_id": "pvt_1a2b3c4d5e",
      "public_relative_path": "contacts/pvt_1a2b3c4d5e.json",
      "file_size_bytes": 48123,
      "message_count": 730
    }
  ]
}
```

## 3. Contact Stats

`tier-contacts` 的输入建议：

```json
{
  "contacts": [
    {
      "public_contact_id": "pvt_1a2b3c4d5e",
      "message_count": 730,
      "active_days": 96,
      "relation_strength": 0.82,
      "topic_tags": ["research", "daily"],
      "relation_tags": ["close_peer"],
      "style_notes": ["direct", "short_replies"]
    }
  ]
}
```

## 4. Tier Output

```json
{
  "tier_counts": {
    "S": 1,
    "A": 1,
    "B": 0,
    "Reference": 1
  },
  "contacts": [
    {
      "public_contact_id": "pvt_1a2b3c4d5e",
      "message_count": 730,
      "active_days": 96,
      "relation_strength": 0.82,
      "tier": "A",
      "score": 0.74,
      "score_breakdown": {
        "volume_score": 0.77,
        "activity_score": 0.53,
        "relation_score": 0.82
      }
    }
  ]
}
```

## 5. Downstream Boundary

下游仓库只应该接收：

- `public_contact_id`
- 分层结果
- 抽象 topic / relation / style tags
- 去敏后的统计摘要

下游仓库不应接收：

- 原始文本全文
- 真实 `wxid`
- 手机号 / 邮箱 / 地址
- 私有数据库或运行时状态

