# Privacy Boundary

## Must Not Be Published

以下内容不能进入公开仓库：

- 原始聊天 JSON / 数据库全文
- 真实联系人姓名、备注、昵称、`wxid`
- 手机号、邮箱、住址、学校/实验室内部标识
- WeChat 安装路径、解密 key、数据库路径
- runtime 日志、pending reply 队列、session 状态

## Safe To Publish

以下内容适合公开：

- 去敏后的 `public_contact_id`
- 联系人分层结果
- 抽象标签，例如 `research`, `close_peer`, `formal`
- 统计值，例如消息条数、活跃天数、分层得分
- 泛化后的目录结构、接口约定、命令行工作流

## Release Checklist

1. 确认没有 `raw_exports/`、`merge_all*.db`、`pending_replies.jsonl`
2. 搜索是否还残留 `wxid_`
3. 搜索是否还残留手机号和邮箱模式
4. 样例中只保留伪造 ID 和抽象标签
5. 如果某字段看起来像真实身份线索，就继续去敏

