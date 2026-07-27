---
name: job-hunting-daily-search
description: |
  Daily multi-platform job search automation with dedup tracking, daily report generation, and JD-tailored resume customization.
  
  Searches 8 platforms (Boss Zhipin, Liepin, Zhaopin, 51job, LinkedIn, Guopin, Lagou, Maimai) across 3 configurable career tracks.
  Automatically deduplicates results via SQLite, tracks new/active/expired status changes, and generates structured daily reports with TOP 3 detailed analysis and full overview tables.
  
  When user provides a JD, reads user's base resume data, analyzes JD keywords, customizes the resume HTML, and outputs a tailored PDF-ready file.

  Trigger keywords: job search, find jobs, daily report, job hunting, resume customization, search positions, 求职, 找工作, 岗位搜索, 简历定制, 日报
agent_created: true
---

# Job Hunting Daily Search — Skill Definition

## Overview

This skill automates daily job hunting across 8 platforms and 3 career tracks. It searches, deduplicates, tracks changes, generates structured daily reports, and produces JD-tailored resumes.

## Prerequisites

**Just install the skill.** Everything else — database creation, automation scheduling, profile setup — is handled automatically during onboarding (Phase 0). No manual config files, no CLI scripts needed.

Users only need to provide their information, either by sending documents or answering guided questions.

Default data directory: `~/job-hunting/` (user's home directory, auto-created on first run). If the user specifies a custom path during onboarding, use that instead.

```
~/job-hunting/
├── personal_info/          # User profile + resume data + template
├── search_config/          # Search criteria
├── daily_reports/          # Daily report output
├── jds/                    # Saved JDs
├── resumes/                # Generated resumes
└── database/
    └── jobs.db             # SQLite tracking DB
```

## Trigger Conditions

Use this skill when:

- User asks to search for jobs, find positions, or generate a daily job report
- User provides a JD and wants a tailored resume
- User mentions "求职搜索", "找工作", "岗位日报", "简历定制", "投简历"
- User asks about their daily job hunting automation status

## Core Workflow

### Phase 0: Onboarding — Data Preparation

**When Phase 0 triggers**: If `references/profile.md` or `personal_info/resume_data.json` is missing or incomplete, guide the user through data preparation FIRST. Do NOT proceed to Phase 1-4 until all three data blocks are ready.

**Data blocks required** (see `references/profile_template.md` and `references/resume_data_template.json` for schemas):

| Block | Content | Schema |
|-------|---------|--------|
| Basic Info | Name, target role, experience, city, preferred platforms | `profile_template.md` §Basic Info |
| Job Preferences | Role keywords, salary range, industries, excluded companies, search tracks | `profile_template.md` §Job Preferences |
| Career Profile | Work experience + project experience (for resume generation) | `resume_data_template.json` |

**Onboarding paths** — offer both, let user pick:

#### Path A: Document Import
User sends files (Markdown, text, PDF, Word) containing their background. Parse the documents, extract all three data blocks automatically, present a summary for user confirmation, then save to the configured paths.

Example: user sends 3 Markdown files → extract basic info, work history, project experience → confirm → save.

#### Path B: Guided Q&A
Ask the user step-by-step questions in three stages. Keep it conversational — one stage at a time:

**Stage 1 — Basic Info** (3-4 questions):
> "Let's set up your profile. I'll ask a few questions."
> 1. Your name (Chinese + English), target role?
> 2. Total years of experience? Current employer (to exclude from search)?
> 3. Target city? Any remote preferences?
> 4. Languages (English level, etc.)?

**Stage 2 — Job Preferences** (4-5 questions):
> 1. What roles are you targeting? (e.g., AI Product Manager, LLM PM)
> 2. Target salary range? (monthly or annual)
> 3. Preferred industries? Any to exclude?
> 4. Company preference? (Big tech / AI unicorn / SOE / all)
> 5. Any companies to exclude?

**Stage 3 — Career Profile** (open-ended):
> "Now tell me about your experience. You can describe it freely, or send documents."
> - Work history: company, role, dates, key achievements
> - Key projects: name, your role, impact
> - Key skills and certifications

After each stage, summarize back and confirm before moving to the next. After all three stages, save:
- `references/profile.md` (or configured path)
- `personal_info/resume_data.json` (or configured path)

**Onboarding complete — agent auto-actions**:
Once all data is saved, the agent automatically:
1. Creates the SQLite database in the user's chosen directory (runs `CREATE TABLE IF NOT EXISTS` inline, no script needed)
2. Sets up the daily 9 AM recurring automation via WorkBuddy scheduling
3. Confirms: "Everything is ready. Your first daily report will run tomorrow at 9 AM."

### Phase 1: Daily Search

1. Read user profile from `references/profile.md` (or configured path) to get search parameters: target roles, salary range, city, excluded companies, career tracks

2. Execute WebSearch across all configured platforms and tracks. Use `query_keyword_groups` for batch efficiency when searching multiple keyword combinations simultaneously.

   **Platform keywords** (8 platforms, with `{city}` from profile):
   - `Boss直聘 {primary_role} {city}`
   - `猎聘 {primary_role} {city} 大模型`
   - `智联招聘 {primary_role} 大模型 {city}`
   - `前程无忧 {primary_role} {city} 大模型` or `51job {primary_role} {city}`
   - `LinkedIn {role_en} {city_en}`
   - `国聘 {primary_role} {city} 国企`
   - `拉勾 {primary_role} {city}`
   - `脉脉 {primary_role} {city} 招聘`

   **Track-specific keywords** (additional 3+ groups):
   - `具身智能 产品经理 {city}`
   - `AI架构师 {city} 传统企业`
   - `国企 AI产品经理 {city}`

3. Extract from search results for each job:
   - Company name
   - Job title
   - Salary range (record "Negotiable" if not listed)
   - **Full URL link** (mandatory — do not omit)
   - Source platform
   - **Link type**: Mark as `[非官方链接]` if the URL points to an aggregator/repost site (not the official platform job page)

4. **Low-result retry rule**: If total valid results across all searches < 5, retry once with alternative keywords:
   - Replace primary role with synonyms (e.g., "大模型产品" → "LLM产品"/"AI平台产品")
   - Add "急聘"/"高薪" modifiers
   - If still < 5 after retry, note in the report: "⚠️ 今日搜索结果较少，已尝试换词重搜"

5. **For top matching candidates (e.g., top 10 by relevance)**: Use WebFetch on the job detail page URL to extract:
   - Post time (e.g., "Posted 2 days ago", "Updated 7/22")
   - Recruiter last active time (e.g., "Active today", "1 day ago", "Active within 3 days")

   WebFetch prompt template: "Extract: 1. Job posting time / last update time 2. Recruiter/HR last active time".
   - If the page requires login or is inaccessible → mark as "详情需手动查看" and **keep the link**.
   - WebFetch failure must NOT block the pipeline — proceed with available data.

### Phase 2: Deduplication & Tracking

1. Open or create SQLite database at configured path (`database/jobs.db`)

2. Schema reference — table `jobs`:

   | Column | Type | Description |
   |--------|------|-------------|
   | id | INTEGER PK | Auto-increment |
   | company | TEXT NOT NULL | Company name |
   | title | TEXT NOT NULL | Job title |
   | salary | TEXT | Salary range |
   | link | TEXT | Job posting URL |
   | platform | TEXT | Source platform |
   | first_seen | TEXT | First discovery date |
   | last_seen | TEXT | Last discovery date |
   | status | TEXT DEFAULT 'active' | active / expired |
   | post_time | TEXT | Job posting time |
   | recruiter_active | TEXT | Recruiter last active time |
   | match_score | INTEGER | Match score 0-100 |
   | match_reason | TEXT | Brief match reason (<50 chars) |
   | notes | TEXT | Notes |

   Unique constraint: `UNIQUE(company, title)`

3. Dedup logic:
   - **New** (company+title not in DB) → INSERT with `first_seen` and `last_seen` set to today
   - **Existing** (found in DB) → UPDATE `last_seen` to today, update `salary` if changed
   - **Expired** (in DB, `last_seen` was yesterday, not found today) → UPDATE `status` to 'expired'

4. Calculate match scores for each new job:
   - Extract keywords from job title and description
   - Compare against user's core skills from profile
   - Assign score 0-100 based on keyword overlap density
   - Write brief match reason (<50 chars) focusing on highest-impact match points

### Phase 3: Generate Daily Report

Write to `daily_reports/YYYY-MM-DD.md`. Use two-part format: TOP 3 detailed + full overview table.

```
# Job Hunting Daily Report - YYYY-MM-DD

> Search time: HH:MM | Platforms: Boss/猎聘/智联/51job/LinkedIn/国聘/拉勾/脉脉
> New today: N | Active total: N | Expired today: N

---

## 🎯 Top 3 Matches Today

### 🥇 1. Company — Role Title
- **Salary**: XXX | **Match Score**: XX%
- **Posted**: XXXX | **Recruiter Active**: XXXX
- **Apply Link**: full URL
- **Match Analysis**: 50 words max, focus on Agent/RAG/LLM experience alignment

### 🥈 ... (same format)

### 🥉 ... (same format)

---

## 📋 All Roles Overview

### 🔥 Track 1 Name (N roles)

| # | Company | Role | Salary | Posted | Recruiter | Match | Apply Link |
|---|---------|------|--------|--------|-----------|-------|------------|

### 🤖 Track 2 Name (N roles)

| # | Company | Role | Salary | Posted | Recruiter | Match | Apply Link |
|---|---------|------|--------|--------|-----------|-------|------------|

### 🏛️ Track 3 Name (N roles)

| # | Company | Role | Salary | Posted | Recruiter | Match | Apply Link |
|---|---------|------|--------|--------|-----------|-------|------------|
```

**Critical formatting rules:**
- URLs must be **full, plain text** — no markdown link syntax — so users can copy-paste directly
- Post time: prefer relative ("1 day ago", "today"), fallback to date ("7/22")
- Recruiter activity: always display if available ("Active today" > "1 day ago" > "within 3 days"). Note "详情需手动查看" if inaccessible
- Match column: format as `XX% one-line reason` (e.g., "90% Agent experience directly relevant")
- TOP 3 get dedicated card-style entries with recruiter activity and match analysis
- All three tracks are presented as separate sections in the overview

**Empty report warning**: If zero valid jobs are found after all searches and retries, generate a minimal report with this warning:

```
# Job Hunting Daily Report - YYYY-MM-DD

⚠️ 今日搜索未返回有效结果

可能原因：
- 搜索关键词受限（平台算法变更）
- 当日无匹配岗位上新
- 平台反爬策略升级

建议：手动访问各平台确认，或调整搜索关键词后重试。
```

### Phase 4: Resume Customization (Triggered by JD)

When user provides a JD (URL or text):

1. Read `personal_info/resume_data.json` for base resume data
2. Analyze JD for key terms: role-specific tech (Agent, RAG, LLM, multimodal, etc.), required experience level, domain keywords
3. Adjust resume content:
   - Reorder experience items to prioritize JD-matching work
   - Rewrite summary bullets to emphasize matching skills
   - Reorder skill tags to surface matching keywords first
   - Add JD-matching labels as visual cues
4. Generate customized HTML using the template
5. Output to `resumes/{Company}_{Role}_resume.html`. **If the file already exists, auto-increment version**: `_v2.html`, `_v3.html`, etc. Never overwrite — user may need to compare against previous versions.
6. Tell user: "Open in browser → Cmd+P → Save as PDF"

## Resume Template Format

The resume template uses `{{PLACEHOLDER}}` syntax (see `references/resume_template.html`):

- `{{NAME}}`, `{{NAME_EN}}`, `{{TITLE}}` — header info
- `{{PHONE}}`, `{{EMAIL}}`, `{{WEBSITE}}`, `{{GITHUB}}` — contact info
- `{{WOSHIPM_SECTION}}` — optional woshipm.com profile link (hidden if empty)
- `{{SUMMARY_ITEMS}}` — key strengths `<li>` items
- `{{EXPERIENCE_ITEMS}}` — work experience blocks
- `{{PROJECT_ITEMS}}` — selected project blocks
- `{{SKILL_ITEMS}}` — skill category blocks
- `{{HONOR_ITEMS}}` — honor/certification `<li>` items
- `{{SCHOOL}}`, `{{MAJOR}}`, `{{DEGREE}}`, `{{EDU_DATE}}` — education

Use `scripts/generate_resume.py` to fill these placeholders from a JSON data file:

```bash
python3 scripts/generate_resume.py \
  --data personal_info/resume_data.json \
  --template references/resume_template.html \
  --output resumes/my_resume
```

## Automation Configuration

To run this skill automatically:

- **Scheduler**: WorkBuddy built-in automation engine
- **RRULE**: `FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=9;BYMINUTE=0`
- **Execution time**: 9:00 AM on weekdays (so HR sees applications first thing)

## References

- `references/profile_template.md` — User profile template; fill in and save as `profile.md`
- `references/daily_report_template.md` — Detailed daily report format reference
- `references/resume_template.html` — HTML resume template with `{{placeholders}}`
- `references/resume_data_template.json` — JSON resume data schema; fill in with your info

## Scripts (Agent-Only)

These are prebuilt for the agent. You never run them manually — WorkBuddy triggers them automatically.

- `scripts/init_db.py` — SQLite tracking database initialization
- `scripts/generate_resume.py` — HTML resume generation from JSON data + template
