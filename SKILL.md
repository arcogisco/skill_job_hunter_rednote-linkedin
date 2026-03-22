---
name: xhs-linkedin-job-search
description: Explicit-invocation 小红书 + LinkedIn job search orchestrator. Use only when the user explicitly calls this skill by full or partial name such as `job-search`, or explicitly asks to在小红书上找 JD、招聘帖、内推帖、refer 线索，并再补 LinkedIn JD 链接。 Default to Chinese output unless the user asks fully in English or explicitly requests English. Search only; never apply, email, or contact recruiters on the user's behalf.
---

# XHS + LinkedIn Job Search

## Overview

Use this skill when the user wants a unified job search workflow that:

- searches Xiaohongshu first for hiring posts, referral posts, refer leads, job-seeking posts with concrete openings, direct-hire clues, or email clues
- searches LinkedIn second for official JD pages, standardized job titles, company names, and LinkedIn job-post or JD links
- merges both sources into an actionable shortlist the user can review and apply to manually

This skill is for search, synthesis, and filtering only.

## Trigger Boundary

Only use this skill when at least one of these is true:

- the user explicitly invokes `$xhs-linkedin-job-search` or clearly names this skill by a distinctive partial name such as `job-search`
- the user explicitly asks to search Xiaohongshu for JD, 招聘帖, 内推帖, refer 线索, or similar hiring signals
- the user explicitly asks for the two-step workflow: Xiaohongshu first, LinkedIn second

Do not use this skill for generic `找工作`, `看机会`, or broad career exploration unless the user clearly points to Xiaohongshu hiring-post retrieval or explicitly invokes this skill.

## Response Language

Default to Chinese in the final user-facing answer.

Only reply fully in English when at least one of these is true:

- the user asked fully in English
- the user explicitly requested an English answer

It is fine to keep keywords, company names, job titles, city names, and other proper nouns in English when that is the clearest form.

Load extra references only when needed:

- use [intake-checklist.md](./references/intake-checklist.md) when validating whether the user's request is specific enough to search
- use [query-expansion.md](./references/query-expansion.md) when generating bilingual search combinations
- use [merge-ranking-rules.md](./references/merge-ranking-rules.md) when matching and ordering results
- use [output-format.md](./references/output-format.md) right before drafting the final answer
- use [cache-policy.md](./references/cache-policy.md) when deciding whether to reuse or update an existing result
- use [examples.md](./references/examples.md) when deciding whether a request should trigger this skill and what a good final answer looks like

If normalization, deduplication, or persistence becomes repetitive, use the helper scripts in `scripts/` instead of re-implementing the logic.

Default result count:

- return `top 10` actionable jobs unless the user asks for a different number

Never:

- apply on behalf of the user
- send email
- DM recruiters
- claim a referral, email, city, or link unless it is explicitly found

If a field is missing, write `未找到`, `未明确`, or `无法判断`.

## Workflow Decision

Use this workflow in the exact order below:

1. collect and validate user search criteria
2. warn if the role direction is too broad
3. search Xiaohongshu first
4. search LinkedIn second
5. merge, deduplicate, filter, and rank
6. output a structured job list in the required format

Do not reverse the search order.
Do not stop after only one source unless the other source truly has no useful results.
Do not return only raw links or raw search dumps.

## Step 1: Intake And Completeness Check

Before searching, extract and check at least:

- target role
- target track or product direction
- target industry
- target city, country, or region
- seniority or years of experience
- company preferences
- whether overseas roles are acceptable
- whether internship, campus hiring, full-time, contract, or other non-full-time roles are acceptable
- storage target for dedupe:
  OpenClaw memory backend when called through OpenClaw API, otherwise a user-provided save path is needed for cross-run dedupe

Use [intake-checklist.md](./references/intake-checklist.md) as the default checklist.

Treat role specificity as a high-priority gate.

Examples:

- `AI PM` is too broad
- `AI Agent PM`, `LLM PM`, `GenAI PM`, `AI Search PM`, `AI Growth PM` are much better

If the role direction is clearly too vague, say so directly before searching.

Use wording like:

`先把岗位方向再收窄一点。AI PM 太泛，AI Agent PM / LLM PM 会准很多。再补充目标国家或城市，我才能更准确地匹配 JD。`

Decision rule:

- If critical fields are missing and the search would be noisy, ask the user to add details first.
- If the request is still searchable but broad, warn once, then continue with best-effort search.

## Step 2: Search Planning

### Intent Refinement

Rewrite the user's request into a search plan that includes:

- specific role variants
- track and domain variants
- city and region variants
- company type variants
- employment-type filters

### Language Strategy

Choose search language by target market, not just by the user's input language.

Rules:

- If the user writes in Chinese and the target market is China or another Chinese-language market:
  use Chinese on Xiaohongshu, and use Chinese plus English expansions on LinkedIn.
- If the user writes in Chinese and the target market is overseas:
  keep Xiaohongshu queries in Chinese for hiring, referral, and overseas Chinese job-seeking context;
  use English role names, industry terms, and city names first on LinkedIn.
- If the user writes in English:
  search both sources in English first unless the user explicitly wants Chinese-speaking posts.

Examples:

- `找美国的 AI 产品经理`
  Xiaohongshu: `美国 AI 产品经理 招聘`, `美国 AI 产品经理 内推`
  LinkedIn: `AI Product Manager`, `GenAI Product Manager`, `LLM Product Manager`, `AI Agent Product Manager`
- `找伦敦的 AI agent 产品经理`
  LinkedIn: `AI Agent Product Manager`, `Generative AI Product Manager`, `Product Manager AI Agents`

### Keyword Expansion

Do semantic expansion before searching.

Use [query-expansion.md](./references/query-expansion.md) when generating expanded query sets.

Company type:

- 外企 -> `外资企业`, `跨国公司`, `MNC`, `foreign company`, `international company`, `global company`
- 大厂 -> `头部互联网`, `big tech`, `top tech company`, `major platform company`
- 独角兽 -> `独角兽`, `unicorn`, `high-growth startup`
- 初创 -> `初创`, `startup`, `early-stage`, `seed`, `series A`, `venture-backed`

Role:

- AI 产品经理 -> `AI PM`, `AI Product Manager`, `Artificial Intelligence Product Manager`, `GenAI PM`, `LLM PM`, `AIGC 产品经理`
- AI Agent 产品经理 -> `AI Agent PM`, `Agent Product Manager`, `AI Agent Product Manager`
- 商业化产品经理 -> `Monetization PM`, `Ads PM`, `Advertising Product Manager`, `Growth Monetization PM`
- 策略产品经理 -> `Strategy PM`, `Optimization PM`, `Recommendation PM`, `Ranking PM`
- 增长产品经理 -> `Growth PM`, `User Growth PM`, `Growth Product Manager`

Industry:

- 科技 / 互联网 -> `Tech`, `Internet`, `Software`, `Platform`, `SaaS`, `Consumer Tech`
- AI -> `Artificial Intelligence`, `GenAI`, `AIGC`, `LLM`, `Agent`, `Machine Learning`
- 广告 -> `Ads`, `Advertising`, `AdTech`, `Monetization`, `Marketing Tech`

City and region:

- 北上广 -> `北京`, `上海`, `广州`
- 江浙沪 -> `上海`, `杭州`, `南京`, `苏州`, `宁波` and nearby core cities
- 湾区 -> `San Francisco Bay Area`, `San Francisco`, `San Jose`, `Mountain View`, `Palo Alto`, `Sunnyvale`
- 海外 -> infer likely markets from context; if still unclear, ask the user to narrow it down

## Step 3: Xiaohongshu Search First

Run the Xiaohongshu stage before LinkedIn.

Use the search patterns and retrieval style from the Rednote skill summarized in [integrations.md](./references/integrations.md), and prioritize:

- 招聘帖
- 内推帖
- refer 帖
- 求职贴中提到的明确岗位
- 华人求职语境中的海外岗位信息
- 团队直招或 HC 信息
- 邮箱投递线索
- 城市线索

Use combinations such as:

- `岗位关键词 + 招聘`
- `岗位关键词 + 内推`
- `岗位关键词 + refer`
- `行业 + 岗位 + 城市`
- `公司类型 + 岗位`
- `公司名称 + 岗位`
- synonym and bilingual expansions when helpful

Prefer posts that explicitly mention:

- company name
- job title
- city
- refer or referral wording
- email or contact clue
- recent timing that still looks valid

For every useful result, extract if available:

- company name
- role name
- short summary of what the role is hiring for
- keywords
- city
- whether referral is explicitly available
- email
- direct Xiaohongshu post link

Important Xiaohongshu link rule:

- Prefer a directly navigable Xiaohongshu note URL captured from the real session or share flow.
- For web `explore/` note links, treat missing `xsec_token` as a serious quality problem.
- If the link does not contain the required signature parameters needed for reliable web access, do not treat it as a high-quality direct link.
- Never invent, synthesize, or guess `xsec_token` or similar signature parameters.

## Step 4: LinkedIn Search Second

Only after Xiaohongshu search is complete, search LinkedIn.

The LinkedIn stage is meant to fill in:

- official job page
- standardized company name
- standardized role title
- LinkedIn job-post or JD link
- job-description keywords
- clearer city and location data

Use English first for overseas roles.

Search combinations:

- English role title
- industry + English role title
- city + English role title
- company type + English role title
- user-specified company + English role title

Extract where possible:

- official LinkedIn job-post or JD link
- standardized company name
- standardized role title
- city
- core JD keywords

Treat the final `LinkedIn 链接` field as the LinkedIn job-post or JD link.
If an external apply link exists, it may be mentioned additionally, but it does not replace the main LinkedIn field.

Follow the safety limits in [integrations.md](./references/integrations.md).
This skill may use the job-hunter capability for search guidance, but it must stay in search-only mode.

## Step 5: Merge And Filter

Merge Xiaohongshu and LinkedIn results using best-effort matching on:

- company name
- role title
- city
- role keywords
- team or business direction

Allow:

- one Xiaohongshu clue matching one LinkedIn job
- one Xiaohongshu clue matching multiple LinkedIn jobs
- a single-source result when the other source is unavailable

Never invent missing data.

If merge fails, keep the entry if it still has action value and clearly mark the missing source.

Use [merge-ranking-rules.md](./references/merge-ranking-rules.md) for normalization, dedupe, and tie-breaking details.
If needed, use `scripts/normalize_job.py` and `scripts/dedupe_jobs.py`.

## Step 6: Match Rules

Check match quality in this order:

1. role match
2. track match
3. industry match
4. company type match
5. city match
6. seniority match
7. language fit
8. extra user constraints

Partial matches are allowed if they are still actionable.
When returning a partial match, mention the deviation in the summary sentence.

Example:

`方向接近 AI Agent PM，但更偏平台侧而非应用侧。`

## Step 7: Ranking Rules

Sort results by:

1. entries that have both a Xiaohongshu post link and a LinkedIn job-post or JD link
2. strong match on role, track, and city
3. explicit referral or email clues
4. newer and still-likely-active posts or jobs
5. completeness of company and role information
6. closeness to the user's stated track

## Step 8: Persistence And Reuse

Avoid repeated search work when the same JD or job clue has already been found recently.

Persistence rules:

- Save previously found jobs in one shared location.
- If the user provides a save path, use that exact location.
- Otherwise, when this skill is called through the OpenClaw API, default to the OpenClaw memory backend.
- If neither OpenClaw memory nor a user-provided save path is available, cross-run dedupe is unavailable.
- If persistent storage is unavailable, still deduplicate only within the current run.

Store enough normalized data to avoid re-fetching the same job unnecessarily:

- source type
- company name
- role title
- city
- keywords
- Xiaohongshu post link
- LinkedIn job-post or JD link
- first seen time
- last seen time

Use these keys to detect duplicates, in order:

1. exact Xiaohongshu post link
2. exact LinkedIn job-post or JD link

Do not deduplicate or overwrite records by `company + role + city` text matching alone, because that can merge different jobs incorrectly.

Reuse policy:

- If an identical result already exists in memory, reuse it instead of treating it as a new job.
- If a cached result is incomplete and a new run finds better fields, update the stored record.
- If two results appear to describe the same job but fields conflict, prefer the source with the more explicit link and clearer city or title.

Use [cache-policy.md](./references/cache-policy.md) for field-level storage rules.
If structured persistence is needed, use `scripts/cache_store.py`.

## Step 9: Failure Handling

Use these fallbacks:

- If Xiaohongshu has results but LinkedIn does not, still return them as Xiaohongshu-only results.
- If LinkedIn has results but Xiaohongshu does not, still return them as LinkedIn-only results.
- If both sources are weak, say result quality is insufficient and advise the user to narrow role direction, city, or track.
- If the user specifies an overseas role but only gives a fuzzy Chinese role title, automatically convert it into English role keywords before LinkedIn search.

## Final Output Format

Do not output a generic summary instead of jobs.
Return a structured job list only.

Use [output-format.md](./references/output-format.md) to keep the final output shape consistent.

Optional delivery rule:

- By default, return the structured result directly in chat only.
- If the user explicitly asks for a doc deliverable, also package the same result into the requested destination.
- Supported destinations are Google Doc, Feishu Doc, or a local file path provided by the user.
- If the user asks for local output but does not provide a path, ask for the save path before writing.

For each result, use this base shape:

```text
[公司名称] - [岗位名称]
一句话概括：[直接概括这个岗位在招什么]
关键词：[关键词1 / 关键词2 / 关键词3]
城市：[城市名 / 国家名 / Remote / 未明确]
Refer：[可 refer / 未明确 / 无法判断]
邮箱：[邮箱地址 / 未提供]
```

Link rule:

- If the result has a Xiaohongshu source, include `小红书链接：[链接]`
- If the result has a LinkedIn source, include `LinkedIn 链接：[链接]`
- If the result has both, include both lines
- Do not force both link lines onto every single result
- Do not invent missing links

Field rules:

- `一句话概括` should say what the role is hiring for and mention any notable mismatch if needed.
- `关键词` should summarize the direction, such as `AI Agent / LLM / Growth / B2B SaaS`.
- `Refer` can only be `可 refer` when explicitly stated in the source.
- `邮箱` can only be filled when explicitly present in the post or JD.

## Success Standard

The output is successful only if:

- it returns actionable job entries rather than generic content
- the user can immediately decide whether to apply
- the user can continue tracking referral, email, city, and link information
- the search order stayed Xiaohongshu first, LinkedIn second
