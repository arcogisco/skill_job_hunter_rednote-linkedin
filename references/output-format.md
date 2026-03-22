# Output Format

The final answer must be a structured job list, not a generic summary.

By default, return the result in chat only.
If the user explicitly asks for a document deliverable, the same content may also be written to:

- Google Doc
- Feishu Doc
- a local file path

If the user explicitly asks for Feishu Bitable output, write the structured results into the target Bitable as records instead of a narrative doc.

For Feishu Bitable:

- `关键词` should be stored as a multi-select field
- split `关键词` by `/` before writing
- `城市` should be stored as a multi-select field
- when one result contains multiple cities, split by `/` before writing
- keep the chat output format unchanged, but split into separate options for Bitable storage

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
- `关键词`: use `3-5` short tags joined by `/`
- each tag should be a short direction, domain, product type, or hiring focus
- good examples: `AI Agent / LLM / Growth / B2B SaaS`
- avoid long clauses, explanations, or full sentences in the keyword field
- user input does not need to already be `/`-joined
- accept spaces, `,`, `，`, `;`, `；`, `|`, `、`, or a natural-language phrase and normalize it into `/`-joined tags
- `Refer`: only use `可 refer` when explicitly stated
- `邮箱`: only fill when explicitly present in the source
- `小红书链接`: only include a directly usable Xiaohongshu post link captured from the real session or share flow
- `LinkedIn 链接`: LinkedIn job-post or JD link

## Xiaohongshu Link Quality

For Xiaohongshu web note links:

- prefer the full signed link
- bare `explore/<note_id>` links may be unusable in the browser
- do not invent or patch in `xsec_token` / `xsec_source`

If a Xiaohongshu link looks incomplete or not safely usable, omit the link line instead of returning a broken placeholder.

## Missing Data Rules

Do not invent:

- refer
- email
- city
- LinkedIn link
- Xiaohongshu link

If a source link does not exist for that result, omit that link line instead of fabricating a placeholder.
