# Output Format

The final answer must be a structured job list, not a generic summary.

## Required Shape

Use this base block per result:

```text
[公司名称] - [岗位名称]
一句话概括：[直接概括这个岗位在招什么]
关键词：[关键词1 / 关键词2 / 关键词3]
城市：[城市名 / 国家名 / Remote / 未明确]
Refer：[可 refer / 未明确 / 无法判断]
邮箱：[邮箱地址 / 未提供]
```

Then add only the link lines that actually exist:

```text
小红书链接：[链接]
```

```text
LinkedIn 链接：[链接]
```

If both sources exist, include both lines.
If only one source exists, include only that one line.

## Field Rules

- `一句话概括`: say what the role is hiring for; if partial match, mention the deviation
- `关键词`: summarize the direction such as `AI Agent / LLM / Growth / B2B SaaS`
- `Refer`: only use `可 refer` when explicitly stated
- `邮箱`: only fill when explicitly present in the source
- `小红书链接`: direct post link if found
- `LinkedIn 链接`: LinkedIn job-post or JD link

## Missing Data Rules

Do not invent:

- refer
- email
- city
- LinkedIn link
- Xiaohongshu link

If a source link does not exist for that result, omit that link line instead of fabricating a placeholder.
