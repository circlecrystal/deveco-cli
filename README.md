# deveco-cli

DevEco Studio 工具链的 Python CLI 封装，提供 **7 条命令**覆盖鸿蒙应用开发全流程，所有输出均为结构化 JSON，可作为 [deveco-mcp](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/ide-deveco-studio) 的轻量替代，适用于脚本自动化与 Agent 驱动场景。

---

## 环境要求

- macOS（DevEco Studio 安装于本机）
- Python ≥ 3.12
- [DevEco Studio](https://developer.huawei.com/consumer/cn/deveco-studio/) 已安装（默认路径 `/Applications/DevEco-Studio.app`）

> **注意：** DevEco Studio 的安装路径及鸿蒙工程路径均不得包含空格。

---

## 安装

```bash
pip install -e .
# 或使用 uv
uv pip install -e .
```

安装后即可使用 `deveco` 命令。

---

## 环境变量

| 变量 | 说明 | 默认值 |
|---|---|---|
| `DEVECO_PATH` | DevEco Studio 安装路径 | `/Applications/DevEco-Studio.app` |
| `ADK_KNOWLEDGE_API` | 知识库搜索 API endpoint | 内置默认地址 |

---

## 命令一览

所有命令均通过 `--project` / `-p` 指定鸿蒙工程根目录，输出为 JSON。

### `build` — 构建 HAP / HSP / HAR

```bash
deveco build --project <path> [--module entry@default] [--intent LogVerification|UIDebug|PerformanceProfile|Release]
```

- 依次执行 `ohpm install` 和 `hvigorw`
- `--module` 缺省时构建整个 APP（`assembleApp`），指定时按模块类型自动选择任务（`assembleHap` / `assembleHsp` / `assembleHar`）
- `--intent` 控制构建模式，默认 `LogVerification`（debug + 不开 debugLine）

**输出示例：**
```json
{
  "status": "ok",
  "command": "build",
  "task": "assembleHap",
  "intent": "LogVerification",
  "hap_files": ["/path/to/entry-default-signed.hap"],
  "message": "构建成功，找到 1 个 HAP 文件"
}
```

---

### `sync` — 项目同步

```bash
deveco build --project <path> [--skip-ohpm] [--product default]
```

执行 `ohpm install`（可跳过）+ `hvigorw --sync`，用于初始化或更新工程依赖。

---

### `check` — ArkTS 静态语法检查

```bash
deveco check --project <path> src/main/ets/pages/Index.ets [更多文件...]
```

通过 DevEco 内置的 `ace-server` 启动 LSP 服务，对指定 `.ets` 文件进行静态分析，返回诊断信息。

**输出示例：**
```json
{
  "status": "ok",
  "command": "check",
  "files_checked": 1,
  "total_issues": 2,
  "diagnostics": {
    "/path/to/Index.ets": [
      {
        "range": {"start": {"line": 10, "character": 4}, "end": {"line": 10, "character": 12}},
        "severity": 1,
        "code": "ts(2322)",
        "message": "Type 'string' is not assignable to type 'number'."
      }
    ]
  },
  "message": "检查完成，2 个问题"
}
```

> severity：`1` = Error，`2` = Warning，`3` = Information，`4` = Hint

---

### `start` — 安装并启动应用

```bash
deveco start --project <path> [--device <设备ID>] [--ability EntryAbility]
```

将 HAP 安装到已连接的设备（或模拟器）并启动指定 Ability。

---

### `ui-tree` — 获取 UI 树

```bash
deveco ui-tree --project <path> --mode simple|full --output-dir <dir> [--device <设备ID>]
```

Dump 当前界面的 UI 组件树并保存到 `--output-dir`，`simple` 模式只保留关键属性，`full` 模式输出完整属性。

---

### `ui-action` — UI 操作

```bash
# 点击
deveco ui-action --project <path> --type click --x 360 --y 640

# 输入文本
deveco ui-action --project <path> --type inputText --x 360 --y 200 --text "Hello"

# 方向滑动
deveco ui-action --project <path> --type directionalFling --direction 3 --velocity 600

# 按键
deveco ui-action --project <path> --type keyEvent --key1 Back

# 截图
deveco ui-action --project <path> --type screenshot --local-path ./screenshot.png
```

支持的操作类型：

| `--type` | 说明 | 必填参数 |
|---|---|---|
| `click` | 点击坐标 | `--x` `--y` |
| `inputText` | 在坐标处输入文字 | `--x` `--y` `--text` |
| `directionalFling` | 方向滑动 | `--direction`（0左/1右/2上/3下）|
| `keyEvent` | 按键事件 | `--key1`（可加 `--key2` `--key3` 组合键）|
| `screenshot` | 截图 | 可选 `--local-path` 保存到本地 |

---

### `knowledge` — 搜索 HarmonyOS 开发文档

```bash
deveco knowledge ArkTS 组件 Text
```

根据关键词搜索鸿蒙开发知识库，返回相关文档片段。可通过 `ADK_KNOWLEDGE_API` 环境变量替换默认 endpoint。

---

## 错误输出格式

所有命令在失败时统一返回以下结构，进程退出码为 `1`：

```json
{
  "status": "error",
  "command": "build",
  "error_type": "build_failed",
  "message": "hvigorw assembleHap 失败（退出码 1）",
  "detail": "...",
  "suggestion": "检查 ArkTS 语法错误，或运行 deveco check 进行静态检查"
}
```

---

## License

MIT
