# 外部模型适配器协议

当前提供模型无关的 JSON 子进程接口，未实现或测试任何特定厂商 API。无需在聊天里发送密钥。适配器自行从用户本机的正常凭据配置读取密钥，调用用户选择的模型。

示例启动形式（适配器文件须先自行实现）：

```bash
python3 -m hesp --mode memory_only --case owner_policy --output runs/model_pilot \
  --planner-command-json '["python3", "/absolute/path/to/trusted_adapter.py"]'
```

控制器启动 argv 对应的程序，不使用 shell。程序从标准输入读取一个 JSON 请求，只在 stdout 输出一个 JSON 对象，正常退出。stderr 不写入研究日志，避免错误信息泄漏凭据。每次调用有 30 秒超时。

输入包括 `protocol`、`mode`、公开 `task`、`tools`、`history` 和剩余调用预算。B/C 还包括 `investigation`，C 包括 `action_rankings`。隐藏答案不在输入中。

执行一个动作：

```json
{"kind":"action","action_id":"inspect_session","reason":"检查当前身份是否仍有效","usage":{"input_tokens":120,"output_tokens":30}}
```

提交最终诊断：

```json
{"kind":"finish","hypothesis":"session_expired","evidence_ids":["o0001"],"reason":"引用实际返回的诊断信号","usage":{"input_tokens":150,"output_tokens":40}}
```

主动停止：

```json
{"kind":"stop","reason":"现有信息不足以继续","usage":null}
```

以上 token 数仅是协议示例，不是本项目的真实用量。适配器必须使用服务端返回的 usage，不可估算或虚构。未提供时，本次运行累计 Token 输出为 null。

## 尚需实现的研究组件

本接口只覆盖动作/结束选择。真实版还需要候选假设生成、结果分类、执行前条件预测三个接口。目前使用手工固定目录，不能称为开放式 LLM 假设推理。

适配器的候选预测调用等费用必须汇总到 usage，包含缓存和推理 Token 的口径需要按选定厂商明确。若服务不支持真实 token 限制，在预算边界可能出现一次调用超支，必须记录而不是宣称硬性零超支。

## 安全说明

子进程不是沙箱，也不限制子进程访问外网。仅执行用户明确提供并信任的适配器。在未确定服务商、模型、预算和运行机器前，不应自动启动付费调用。
