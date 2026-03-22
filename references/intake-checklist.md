# Intake Checklist

Use this checklist before any search begins.

## Required Checks

Extract and assess:

- target role
- role direction or specialization
- target track or product direction
- target industry
- target city, country, or region
- seniority or years of experience
- company preference
- whether overseas roles are acceptable
- whether internship, campus hiring, full-time, contract, part-time, or other non-full-time roles are acceptable

## High-Priority Gate

Check whether the role direction is specific enough.

Examples of weak input:

- `AI PM`
- `产品经理`
- `运营`

Examples of stronger input:

- `AI Agent PM`
- `LLM PM`
- `GenAI PM`
- `AI 搜索 PM`
- `商业化产品经理`
- `推荐策略产品经理`

## Decision Rules

Ask the user to refine the request before searching if either of these is true:

- the role direction is too broad to produce useful results
- the target geography is too vague for LinkedIn search

Warn once but continue with best effort if:

- the role is broad but still searchable
- the city list is broad but still bounded
- the user omitted lower-priority preferences such as company type

## Direct Reminder Template

Use concise wording.

Examples:

- `先把岗位方向再收窄一点。AI PM 太泛，AI Agent PM / LLM PM 会准很多。`
- `再补充目标国家或城市，我才能更准确地匹配 JD。`
- `如果你接受海外岗位，也请限定到美国 / 英国 / 新加坡这种范围，不然结果会太散。`
