# Pipeline Handoff

这个仓库的终点，是为下游仓库准备一份结构化、安全化的输入。

## Recommended Handoff Files

建议传给 `Distill_myself_RAG-Skill` 的文件：

1. `export_manifest.redacted.json`
2. `contact_tiers.json`
3. `pipeline_handoff.md`

## Minimal Handoff Contract

下游最少需要这些字段：

- `public_contact_id`
- `tier`
- `message_count`
- `topic_tags`
- `relation_tags`
- `style_notes`

## Why This Split Exists

拆成两个仓库的原因：

- `wechat` 仓库负责导出后的清洗、去敏、分层
- `pipeline` 仓库负责把清洗结果变成 RAG 文档、skill 模板和自动化接口

这样做有两个好处：

1. 隐私边界更清晰
2. skill 逻辑可以被复用到其他个人知识蒸馏任务，而不绑定微信原始导出过程

