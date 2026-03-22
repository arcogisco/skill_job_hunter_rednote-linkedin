# XHS Job Search 🔎

Search job opportunities on Xiaohongshu and return a structured list you can directly screen.  
在小红书里捞招聘帖、内推帖和 refer 线索，再整理成可直接筛选的岗位清单。

## What It Does | 这是做什么的 ✨

A **job search skill**. It **does not apply**, **does not send emails**, and **does not contact recruiters**.  
一个**找岗位**的 skill。**不代投，不发邮件，不替用户外联。**

## Core Flow | 核心流程 🚀

**Search XHS → extract structured fields → return clean results**  
**先搜小红书 → 提取结构化字段 → 输出结果**

提取的信息包括：公司名称、岗位名称、一句话概括、关键词、城市、Refer、邮箱、小红书链接。  
如果用户明确要求，也可以继续整理成 doc 或写入 Feishu Bitable。

## Quick Start | 快速开始 ⚡

```text
用 job-search 帮我找伦敦的 GenAI PM
用 job-search 帮我找上海的项目经理，并整理到飞书多维表格
用 job-search 帮我找北京的junior PE岗位，并输出到Feishu
```

## Best For | 适用场景 🎯
Explicit skill call: $xhs-job-search 直接调用 skill
Partial skill name: job-search 只说部分名字
XHS hiring search: 招聘帖 / 内推帖 / refer 线索
Clear target: 目标相对明确的岗位搜索

AI Agent PM usually works better than AI PM. AI Agent PM 通常会比 AI PM 更准。

## Response Language | 回复语言 🌍
Default: Chinese 默认中文
English if requested: 用户全英文提问或明确要求英文时切换
Keep role/company names in English: 岗位名、公司名、关键词保留英文没问题

## Output Format | 输出格式 📄

**Structured, clean, and directly scannable**  
**结构化输出，方便直接筛选**

每条结果统一整理成下面这样：

```text
[公司名称] - [岗位名称]  
一句话概括：[直接概括这个岗位在招什么]  
关键词：[关键词1 / 关键词2 / 关键词3]  
城市：[城市名 / 国家名 / Remote / 未明确]  
Refer：[可 refer / 未明确 / 无法判断]  
邮箱：[邮箱地址 / 未提供]  
小红书链接：[链接 / 未找到]
```

## Notes | 说明 📝

**Honest output only**  
**如实返回，不编造字段**

尽量返回真正能点开的 XHS 链接。  
如果只是裸的 `explore/<note_id>`，没有签名参数，就不要硬塞进结果里。

## Optional Output | 可选产出 📦

**Chat first, docs if requested**  
**默认对话返回，用户明确要求时再产出文档**

支持的产出形式包括：Google Doc、Feishu Doc、本地文件、Feishu Bitable。  
当前最稳的集成是 **Feishu Bitable**。

## Feishu Bitable | 飞书多维表格 📊

**Default target: `job_hunter_rednote / Jobs`**  
**默认目标：`job_hunter_rednote / Jobs`**

支持的输入方式包括：已有 Bitable 链接、`app_token + table_id`、Feishu `App ID / App Secret`。  
当前更稳的路径是：**复用已有表**，或**在已有 base 下新建一张表再写入**。

如果缺少 Feishu API 凭证，需要先提醒用户提供。

## Dedup Logic | 去重逻辑 🧹

**Exact-link only**  
**只按完全相同的链接去重**

不做 `company + role + city` 这类模糊去重，避免误伤。

## Why It’s Useful | 这个 skill 的优点 💡

**Real hiring signals, fixed fields, clean flow**  
**真实招聘线索，固定字段，流程清晰**

它能拿到小红书里的真实招聘线索，输出字段固定，后面继续筛选很方便。  
整体流程也比较清楚，不容易乱跑。





