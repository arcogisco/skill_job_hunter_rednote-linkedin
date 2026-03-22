# External Integrations

This skill combines two outside capabilities, but keeps a narrower scope than either one.

## Xiaohongshu Side

Source:

- `https://github.com/Giselle-123/rednote_search_skill`

What to inherit from that skill:

- Xiaohongshu-first retrieval mindset
- query rewrite before search
- structured field extraction
- direct post links as a required output field
- concise, data-first presentation

How to use it in this orchestrator:

- Search Xiaohongshu first.
- Prefer Chinese queries unless the user clearly wants English-speaking content.
- Search for `招聘`, `内推`, `refer`, team hiring clues, city clues, and email clues.
- Reuse its behavior of preferring direct, navigable post links over vague mentions.

## LinkedIn Side

Source:

- `https://clawhub.ai/sharbelayy/job-hunter`

Important safety note:

- The public ClawHub page for `job-hunter` is flagged as suspicious.
- The page says the bundle includes scripts that can call external services and use `BRAVE_API_KEY`.
- The public README also describes broader behaviors such as evaluating jobs, application support, cover letters, salary research, interview prep, and tracking.

This orchestrator must not inherit the full behavior set.

Allowed use:

- use the capability only to search and standardize LinkedIn job information
- use it to help find official LinkedIn job-post or JD pages and extract company, title, location, and JD keywords
- use role expansion ideas for broader search coverage

Disallowed use:

- do not apply to jobs
- do not send email
- do not contact recruiters
- do not run any autonomous outreach
- do not claim to have completed an application
- do not rely on undeclared external API access as a requirement

Preferred LinkedIn search focus:

- official LinkedIn job-post or JD page
- job title normalization
- company normalization
- city normalization
- JD keyword extraction

## Persistence Default

For duplicate avoidance and search-efficiency:

- prefer saving normalized results into the OpenClaw memory backend when this skill is invoked through the OpenClaw API
- if the user provides a custom save path, that overrides the default memory location
- keep enough structured fields to match by link first, then by normalized company, role, and city

If the LinkedIn side is unavailable or low confidence, still return useful Xiaohongshu-only leads and clearly mark LinkedIn as missing.
