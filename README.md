# Distill Myself WeChat History Extrate

面向个人微信数据蒸馏前的本地整理仓库：聚焦聊天记录导出后的结构化扫描、去敏、联系人分层，以及给下游 skill / RAG 流程准备公开安全的输入。

[English README](README_EN.md)

## Overview

这个仓库不是“把真实聊天记录直接丢上 GitHub”。

它公开的是一套可以复用的工作流骨架：

1. 对本地导出结果做目录级扫描。
2. 把联系人标识、文件名、账号痕迹和文本片段做去敏。
3. 用统一评分规则做联系人分层。
4. 产出交给下游仓库 `Distill_myself_RAG-Skill` 的安全化输入。

公开版默认不包含：

- 原始聊天记录
- 真实联系人姓名 / 昵称 / wxid
- SQLCipher key、数据库副本、设备路径
- 任何可逆恢复到真实身份的私人标签

## Highlights

- 提供 `scan-export-root` 命令，把任意导出目录整理成统一 manifest
- 提供 `redact-manifest` 命令，把路径、ID、文本片段统一去敏
- 提供 `tier-contacts` 命令，为联系人打分并分到 `S / A / B / Reference`
- 提供 `build-handoff` 命令，生成给下游 skill/RAG 仓库使用的交接摘要
- 自带样例配置与样例数据结构，便于替换成你自己的本地流程

## Repository Layout

```text
Distill_myself_wechat_history_extrate/
├── docs/
│   ├── data_schema.md          # 公开版数据契约
│   ├── pipeline_handoff.md     # 与下游仓库的衔接方式
│   └── privacy_boundary.md     # 去敏边界与开源注意事项
├── sample_data/
│   ├── contact_stats.example.json
│   └── export_manifest.example.json
├── src/
│   └── wechat_history_extrate/
│       ├── cli.py              # CLI 入口
│       ├── export_scanner.py   # 导出目录扫描
│       ├── redaction.py        # 去敏规则
│       └── tiering.py          # 联系人分层
├── LICENSE
├── README.md
├── README_EN.md
└── pyproject.toml
```

## Workflow

### 1. 扫描导出目录

假设你已经通过自己的本地工具把微信数据导出到如下结构：

```text
export_root/
├── contacts/
│   ├── someone.json
│   └── another_one.json
└── groups/
    └── study_group.json
```

先把目录扫描成一个统一 manifest：

```bash
wechat-release scan-export-root --export-root ./export_root --output ./analysis/export_manifest.json
```

这一步只读取目录、文件大小、可选的消息条数，不要求公开任何真实内容。

### 2. 去敏

```bash
wechat-release redact-manifest --input ./analysis/export_manifest.json --output ./analysis/export_manifest.redacted.json
```

输出会：

- 用哈希后的 `public_contact_id` 替代真实标识
- 用占位符替代 `wxid`、手机号、邮箱、备注名
- 把原始相对路径改写成公开安全路径

### 3. 联系人分层

`contact_stats` 建议至少包含：

- `message_count`
- `active_days`
- `relation_strength`，范围 `0.0 ~ 1.0`

评分公式：

```text
volume_score   = min(log(1 + message_count) / log(1 + 5000), 1)
activity_score = min(active_days, 180) / 180
relation_score = clamp(relation_strength, 0, 1)

final_score = 0.50 * volume_score
            + 0.30 * activity_score
            + 0.20 * relation_score
```

分层阈值：

- `S`: `score >= 0.80`
- `A`: `0.62 <= score < 0.80`
- `B`: `0.42 <= score < 0.62`
- `Reference`: 其余联系人或仅参考对象

运行：

```bash
wechat-release tier-contacts --input ./sample_data/contact_stats.example.json --output ./analysis/contact_tiers.json
```

### 4. 交给下游仓库

```bash
wechat-release build-handoff \
  --manifest ./analysis/export_manifest.redacted.json \
  --tiers ./analysis/contact_tiers.json \
  --output ./analysis/pipeline_handoff.md
```

这份交接文件就是给 [`Distill_myself_RAG-Skill`](https://github.com/HIT-JimmyXiao/Distill_myself_RAG-Skill) 的输入摘要。

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .

wechat-release init-layout --workspace ./demo_workspace
wechat-release write-sample-config --workspace ./demo_workspace
wechat-release scan-export-root --export-root ./demo_workspace/mock_export --output ./demo_workspace/analysis/export_manifest.json
wechat-release redact-manifest --input ./demo_workspace/analysis/export_manifest.json --output ./demo_workspace/analysis/export_manifest.redacted.json
wechat-release tier-contacts --input ./sample_data/contact_stats.example.json --output ./demo_workspace/analysis/contact_tiers.json
wechat-release build-handoff --manifest ./demo_workspace/analysis/export_manifest.redacted.json --tiers ./demo_workspace/analysis/contact_tiers.json --output ./demo_workspace/analysis/pipeline_handoff.md
```

如果你在 Windows 的中文路径下运行，且终端对相对路径解析出现编码异常，优先直接传绝对路径。

## Data Contract

公开版只约定结构，不约定你的私有导出工具。

- 允许你在本地接入 PyWxDump 或其他导出器
- 本仓库只消费“导出后的文件结构或统计结果”
- 所有对外示例都必须是伪造、抽象或去敏后的样例

详细字段见 [docs/data_schema.md](docs/data_schema.md)。

## Privacy Boundary

开源前至少检查：

1. `git status` 里不应出现原始导出目录
2. 任何 `wxid_*`、手机号、邮箱、备注名都应被替换
3. 不要提交数据库、key、缓存、日志、runtime 状态
4. 样例数据只能保留统计值、标签和抽象化说明

详细说明见 [docs/privacy_boundary.md](docs/privacy_boundary.md)。

## Downstream Repository

这个仓库只解决“安全化输入”的问题。

如果你想继续把联系人分层结果转成 RAG 文档、Codex skill 模板和自动化流程，请继续使用：

- [Distill_myself_RAG-Skill](https://github.com/HIT-JimmyXiao/Distill_myself_RAG-Skill)
