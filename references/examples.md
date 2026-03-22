# Examples

Use these examples to decide:

- whether this skill should trigger
- when to ask the user for more detail first
- what a good final output looks like

## Good Trigger Examples

These should trigger this skill directly.

Trigger rule reminder:

- explicit skill invocation is always okay
- distinctive partial skill naming such as `job-search` is also okay
- explicit Xiaohongshu JD / 招聘帖 / 内推帖 retrieval is okay
- vague job-search intent alone is not enough

Language rule reminder:

- default final answer language is Chinese
- switch to full English only when the user asks fully in English or explicitly requests English
- English keywords and proper nouns can stay in English inside Chinese answers

### Example 1

User:

`帮我找美国的 AI Agent 产品经理岗位，先搜小红书再搜 LinkedIn，优先西海岸，3-5 年经验，最好是外企或高增长 startup。`

Why this is good:

- role direction is specific
- market is clear
- city range is bounded
- seniority is clear
- company preference is clear

Expected behavior:

- search Xiaohongshu first with Chinese query sets
- search LinkedIn second with English role and city variants
- return a top 10 structured job list

### Example 2

User:

`找上海或杭州的商业化产品经理，偏广告/变现方向，社招，最好有内推线索。`

Why this is good:

- role direction is specific enough
- track is specific
- city is bounded
- hiring type is clear

Expected behavior:

- prioritize Xiaohongshu posts mentioning refer, 内推, 邮箱, 城市
- use LinkedIn second to补标准岗位名和 JD 链接

### Example 3

User:

`Find GenAI product manager jobs in London. Search Xiaohongshu first for referral-style leads, then LinkedIn for JD links. Prefer B2B SaaS and series A to C startups.`

Why this is good:

- English request is explicit
- role, city, and company type are all bounded
- search order is already aligned with this skill

### Example 4

User:

`帮我找新加坡的 AI Agent PM，最好是面向企业服务或 developer tools 的方向，3-5 年经验，接受独角兽和外企。`

Why this is good:

- role direction is very specific
- market is clear
- domain preference is clear
- seniority and company type are both clear

Expected behavior:

- Xiaohongshu side should still search Chinese hiring and 内推语境
- LinkedIn side should prioritize `AI Agent Product Manager`, `Developer Tools Product Manager`, `Enterprise AI Product Manager`, `Singapore`
- return structured jobs even if some entries only have one source

### Example 5

User:

`找伦敦的 AI 商业化产品经理，偏广告变现或 growth monetization，优先外企和大厂。`

Why this is good:

- role is specific enough
- city is explicit
- track is explicit
- company preference is explicit

Expected behavior:

- expand to `Monetization PM`, `Ads PM`, `Advertising Product Manager`, `Growth Monetization PM`
- rank jobs higher when both Xiaohongshu and LinkedIn links exist

### Example 6

User:

`帮我找在美国的华人求职语境里的 LLM PM 机会，先看小红书上有没有内推或团队直招，再补 LinkedIn JD。`

Why this is good:

- explicitly asks for the two-source workflow
- clarifies overseas-Chinese context on Xiaohongshu
- role direction is specific

Expected behavior:

- Xiaohongshu should prioritize `美国 LLM PM 内推`, `美国 AI 产品经理 招聘`, `团队直招`, `refer`
- LinkedIn should prioritize English role titles and US city or market variants
- final output should preserve Xiaohongshu clues even when LinkedIn cannot fully match

### Example 7

User:

`用 $xhs-linkedin-job-search 帮我找伦敦的 GenAI PM，先搜小红书，再补 LinkedIn。`

Why this is good:

- explicit skill invocation
- explicit search order
- bounded role and city

### Example 8

User:

`用 job-search 帮我找新加坡 AI Agent PM，先搜小红书有没有内推，再补 LinkedIn。`

Why this is good:

- partial skill naming is still explicit enough
- Xiaohongshu-first intent is explicit
- role and market are bounded

Expected behavior:

- trigger this skill
- answer in Chinese
- keep role keywords like `AI Agent PM` in English if clearer

## Non-Trigger Examples

These should not trigger this skill unless the user clarifies or explicitly invokes it.

### Example 9

User:

`帮我找工作。`

Why this should not trigger:

- generic job-search intent only
- no Xiaohongshu retrieval intent
- no explicit skill invocation

### Example 10

User:

`看看最近适合我的机会。`

Why this should not trigger:

- broad exploration only
- does not explicitly ask for Xiaohongshu hiring-post search

## Ask-First Examples

These should not immediately start a noisy search.

### Example 11

User:

`帮我找 AI PM 的工作。`

Why this is not enough:

- role is too broad
- no city or market
- no industry or company preference

Expected response:

- ask the user to narrow role direction
- suggest examples like `AI Agent PM`, `LLM PM`, `GenAI PM`

### Example 12

User:

`我想看海外机会。`

Why this is not enough:

- geography is too broad
- no role direction
- no seniority

Expected response:

- ask for role direction first
- ask the user to narrow geography to US, UK, Singapore, Europe, and so on

### Example 13

User:

`帮我找产品经理机会，最好大厂。`

Why this is not enough:

- role is too broad
- no track
- no market or city
- company preference alone is not enough

Expected response:

- ask for role specialization first
- ask for geography second
- explain that direction specificity matters more than company size alone

## Warn-Then-Search Examples

These can still be searched after one direct warning.

### Example 14

User:

`找美国的 AI 产品经理。`

Why this is borderline:

- market is clear
- role is still broad

Expected response:

- warn that `AI 产品经理` is too wide
- continue with expanded role variants such as `AI Product Manager`, `GenAI PM`, `LLM PM`, `AI Agent PM`

### Example 15

User:

`找新加坡的 PM 岗位，先搜一下。`

Why this is borderline:

- city is clear
- role direction is still broad

Expected response:

- warn once that `PM` 太泛
- continue with broad-but-bounded search if the user does not refine further
- rank more specific AI, growth, monetization, or platform PM matches lower unless they clearly fit other stated preferences

### Example 16

User:

`Use job-search to find AI agent product manager roles in London. Search Xiaohongshu first, then LinkedIn. Reply in English.`

Why this is good:

- partial skill naming is explicit enough
- user asked fully in English
- user explicitly requested English output

Expected behavior:

- trigger this skill
- return the final answer in English
- still preserve Chinese Xiaohongshu search logic where useful

### Example 17

User:

`用 job-search 帮我找美国的 LLM PM，回复英文。`

Why this is good:

- partial skill naming is explicit enough
- explicit English-output request overrides the default Chinese-output rule

Expected behavior:

- trigger this skill
- return the final answer in English

## Keyword Intake Examples

These examples show how to handle users who do not format keywords as tags.

### Example 18

User:

`帮我看看北京外企的 AI 产品经理机会，最好 junior 一点。`

Why this is useful:

- the user did not provide `/`-joined tags
- the input is still specific enough to extract role, city, company type, and seniority signals

Expected behavior:

- do not ask the user to reformat into keyword tags
- extract compact tags such as `AI 产品经理 / 外企 / 北京 / Junior`
- keep the final output keyword field normalized with `/`

### Example 19

User:

`AI产品经理 外企 北京`

Why this is useful:

- input is space-separated instead of `/`-joined
- still contains clear role, company type, and city hints

Expected behavior:

- parse the space-separated input directly
- normalize it into compact keyword tags before search and output

### Example 20

User:

`ai pm；tech；junior`

Why this is useful:

- input uses Chinese semicolons and English abbreviations
- the user intent is still easy to interpret

Expected behavior:

- accept `；` as a valid separator
- keep compact tags such as `AI PM / Tech / Junior`
- do not ask the user to rewrite the input unless core fields are still missing

### Example 21

User:

`找新加坡做企业服务 AI agent 的产品经理，最好 3 年左右经验。`

Why this is useful:

- the user gave one natural-language sentence, not explicit tags
- it still contains enough signals to extract role direction, market, track, and seniority

Expected behavior:

- infer tags such as `AI Agent / 企业服务 / 新加坡 / 1-3 年`
- search directly after extraction
- keep the final keyword field standardized with `/`

### Example 22

User:

`我想找 tech 的 pm。`

Why this still needs a follow-up:

- input is short and easy to parse, but the role direction is still too broad
- `tech` and `pm` alone are not enough for high-quality matching

Expected response:

- do not ask the user to reformat the keywords
- instead ask the user to narrow the role direction, for example `AI PM`, `Growth PM`, `Monetization PM`, `Platform PM`

## Cache Reuse Example

This is the desired reuse behavior.

### Example 23

Situation:

- a previous run already stored a job with the exact same LinkedIn link
- the new run finds the same role again, but this time also finds a Xiaohongshu post with refer clues

Expected behavior:

- do not create a duplicate job entry
- update the existing record
- keep the stronger combined result with both links
- refresh `last_seen_at`

### Example 24

Situation:

- two jobs have very similar company name, role title, and city
- but their links are different

Expected behavior:

- do not deduplicate them just because the text looks similar
- keep them as separate jobs unless the exact same source link appears

## Xiaohongshu Link Quality Example

### Example 25

Situation:

- a Xiaohongshu result only has a bare web link like `https://www.xiaohongshu.com/explore/<note_id>`
- the signed parameters required for browser access are missing

Expected behavior:

- do not present that URL as a high-quality direct post link
- prefer the real signed link captured from the session or share flow
- if a reliable direct link is unavailable, omit the Xiaohongshu link line instead of fabricating parameters

## Good Final Output Example

This is the target output shape.

```text
[Anthropic] - Product Manager, AI Platform
一句话概括：这个岗位在招面向 AI 平台能力建设的产品经理，方向接近 AI Agent PM，但更偏平台能力与开发者生态。
关键词：[AI Platform / LLM / Developer Product]
城市：[San Francisco / United States]
Refer：[未明确]
邮箱：[未提供]
小红书链接：[https://www.xiaohongshu.com/example]
LinkedIn 链接：[https://www.linkedin.com/jobs/view/example]
```

## Bad Output Examples

These are not acceptable final answers.

### Bad Example 1

`我帮你找了一些岗位，感觉都还不错，你可以看看下面这些链接。`

Why this is bad:

- not structured
- no field extraction
- no city, refer, or email status

### Bad Example 2

`目前没有完全匹配，我就不返回任何内容了。`

Why this is bad:

- partial matches can still be useful
- should return actionable near-matches if available

### Bad Example 3

`我已经替你申请了几个岗位。`

Why this is bad:

- violates the no-apply rule
- violates the no-contact rule
