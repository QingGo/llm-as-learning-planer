# LLM 学习计划生成器

一个基于大语言模型的个性化学习计划生成工具，能够根据用户的技术背景和学习目标，生成符合 SMART 原则的双周粒度学习计划，并进一步细化为日粒度学习安排。

## 🌟 核心功能

- 🎯 根据用户背景和目标生成个性化学习计划
- 🔍 对初始计划进行批判性审查，生成多个修正方案
- 📊 对比分析多个方案，生成最优最终计划
- 📅 基于最终计划生成详细的日粒度学习安排
- 🌐 支持多种大模型平台（DeepSeek、Google Generative AI）
- 📝 结构化输出（Markdown + JSON 格式）
- 📋 命令行交互界面
- 📚 完整的日志记录

## 🚀 快速开始

### 1. 安装依赖

```bash
uv venv && uv pip install -e .
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，并填写 API 密钥等配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置大模型 API 密钥：

```env
# 大模型配置
PLATFORM=deepseek  # 可选值: deepseek, google
MODEL_NAME=deepseek-chat
API_KEY=your_api_key_here
```

### 3. 准备输入文件

创建两个文本文件：

- `background.txt`：包含你的技术背景介绍
- `goal.txt`：包含你的学习目标

示例：

**background.txt**
```
我是一名前端开发工程师，有2年React开发经验，熟悉JavaScript和TypeScript，了解基本的后端知识。
```

**goal.txt**
```
我想在3个月内掌握全栈开发技能，能够独立开发完整的Web应用。
```

### 4. 生成学习计划

```bash
source .venv/bin/activate && python -m src.cli generate --background-file background.txt --goal-file goal.txt --output-dir plans
```

### 5. 查看生成结果

生成的计划将保存在指定的输出目录中：

- `plans/overall_plan.md`：最终双周学习计划
- `plans/overall_plan.json`：JSON格式的最终计划
- `plans/daily/`：日粒度学习计划（按双周划分）

## 📖 技术文档

详细的技术设计文档请查看：

[技术设计文档](./docs/technical-design.md)

## 🛠️ 命令行参数

```
planer generate [OPTIONS]

选项：
  --background-file, -bf TEXT  包含个人技术背景介绍的文件路径  [默认: background.txt]
  --goal-file, -gf TEXT        包含学习目标的文件路径  [默认: goal.txt]
  --output-dir, -o TEXT        输出目录，默认使用配置文件中的值
  --verbose, -v                启用详细日志输出
  --help                       显示帮助信息
```

## 📁 项目结构

```
llm-as-learning-planer/
├── src/                     # 源代码目录
│   ├── cli.py               # 命令行界面
│   ├── config.py            # 配置管理
│   ├── model_client.py      # 模型客户端
│   ├── prompt_manager.py    # 提示管理器
│   └── workflow.py          # 工作流定义
├── prompts/                 # Prompt 模板目录
├── docs/                    # 文档目录
├── logs/                    # 日志输出目录
├── plans/                   # 计划输出目录
├── .env                     # 环境变量配置
├── .env.example             # 环境变量示例
├── background.txt           # 背景示例文件
├── goal.txt                 # 目标示例文件
└── README.md                # 项目说明文档
```

## 🎨 支持的大模型平台

- **DeepSeek**：使用 DeepSeek API
- **Google Generative AI**：使用 Google Gemini API

## 📝 配置项说明

| 配置项 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| PLATFORM | str | deepseek | 大模型平台 |
| MODEL_NAME | str | deepseek-chat | 模型名称 |
| API_KEY | str | 必填 | 大模型 API 密钥 |
| LOG_LEVEL | str | INFO | 日志级别 |
| LOG_DIR | str | logs | 日志目录 |
| LOG_TO_FILE | bool | True | 是否输出日志到文件 |
| OUTPUT_DIR | str | plans | 计划输出目录 |

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📞 联系方式

如有问题或建议，欢迎通过 GitHub Issues 反馈。