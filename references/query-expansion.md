# Query Expansion

Use semantic expansion before any source search.

## Keyword Intake

The user does not need to provide perfectly formatted keyword tags.

Accept all of these as valid input styles:

- natural-language phrases such as `找北京外企 AI 产品经理`
- space-separated text such as `AI产品经理 外企 北京`
- mixed punctuation such as `ai pm；tech；junior`
- other loose separators such as `|`, `,`, `，`, `、`

Before expansion:

- extract the role, company type, city, seniority, and domain signals from the user's wording
- normalize them into compact keyword tags
- use `/` as the final normalized separator in output and Feishu storage

## Company Type Expansion

- 外企 -> `外资企业`, `跨国公司`, `MNC`, `foreign company`, `international company`, `global company`
- 大厂 -> `头部互联网`, `big tech`, `top tech company`, `major platform company`
- 独角兽 -> `独角兽`, `unicorn`, `high-growth startup`
- 初创 -> `初创`, `startup`, `early-stage`, `seed`, `series A`, `venture-backed`

## Role Expansion

- AI 产品经理 -> `AI PM`, `AI Product Manager`, `Artificial Intelligence Product Manager`, `GenAI PM`, `LLM PM`, `AIGC 产品经理`
- AI Agent 产品经理 -> `AI Agent PM`, `Agent Product Manager`, `AI Agent Product Manager`
- 商业化产品经理 -> `Monetization PM`, `Ads PM`, `Advertising Product Manager`, `Growth Monetization PM`
- 策略产品经理 -> `Strategy PM`, `Optimization PM`, `Recommendation PM`, `Ranking PM`
- 增长产品经理 -> `Growth PM`, `User Growth PM`, `Growth Product Manager`

## Industry Expansion

- 科技 / 互联网 -> `Tech`, `Internet`, `Software`, `Platform`, `SaaS`, `Consumer Tech`
- AI -> `Artificial Intelligence`, `GenAI`, `AIGC`, `LLM`, `Agent`, `Machine Learning`
- 广告 -> `Ads`, `Advertising`, `AdTech`, `Monetization`, `Marketing Tech`

## City And Region Expansion

- 北上广 -> `北京`, `上海`, `广州`
- 江浙沪 -> `上海`, `杭州`, `南京`, `苏州`, `宁波`
- 湾区 -> `San Francisco Bay Area`, `San Francisco`, `San Jose`, `Mountain View`, `Palo Alto`, `Sunnyvale`

If the user says `海外`, infer from context if possible.
If the likely market is still unclear, ask the user to narrow it.

## Source-Specific Query Patterns

### Xiaohongshu

Prefer Chinese-first combinations such as:

- `岗位关键词 + 招聘`
- `岗位关键词 + 内推`
- `岗位关键词 + refer`
- `行业 + 岗位 + 城市`
- `公司类型 + 岗位`
- `公司名 + 岗位`

### LinkedIn

Prefer English-first combinations for overseas markets:

- `English role title`
- `industry + English role title`
- `city + English role title`
- `company type + English role title`
- `company name + English role title`
