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

Before using this skill, the following must be set up:

1. **User profile** — Fill in `references/profile_template.md` with target user's info (role, salary, city, excluded companies, etc.) and save as `references/profile.md`
2. **Database** — Run `scripts/init_db.py --db-path <path>` to create the SQLite tracking database
3. **Resume data** — Fill in `references/resume_data_template.json` with base resume data
4. **Resume template** — Use `references/resume_template.html` or provide a custom HTML template with `{{PLACEHOLDER}}` syntax
5. **WorkBuddy automation** — Configure a recurring automation with RRULE: `FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=9;BYMINUTE=0`

Data directory structure (user-configurable paths):

```
job-hunting/
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

4. **For top matching candidates (e.g., top 10 by relevance)**: Use WebFetch on the job detail page URL to extract:
   - Post time (e.g., "Posted 2 days ago", "Updated 7/22")
   - Recruiter last active time (e.g., "Active today", "1 day ago", "Active within 3 days")

   WebFetch prompt template: "Extract: 1. Job posting time / last update time 2. Recruiter/HR last active time". If the page requires login or is inaccessible, note "Login required".

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
- Recruiter activity: always display if available ("Active today" > "1 day ago" > "within 3 days"). Note "Login required" if inaccessible
- Match column: format as `XX% one-line reason` (e.g., "90% Agent experience directly relevant")
- TOP 3 get dedicated card-style entries with recruiter activity and match analysis
- All three tracks are presented as separate sections in the overview

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
5. Output to `resumes/{Company}_{Role}_resume.html`
6. Tell user: "Open in browser → Cmd+P → Save as PDF"

## Resume Template Format

The resume template uses `{{PLACEHOLDER}}` syntax (see `references/resume_template.html`):

- `{{NAME}}`, `{{NAME_EN}}`, `{{TITLE}}` — header info
- `{{PHONE}}`, `{{EMAIL}}`, `{{WEBSITE}}`, `{{GITHUB}}` — contact info
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

## Scripts

- `scripts/init_db.py` — Initialize the SQLite tracking database
- `scripts/generate_resume.py` — Generate HTML resume from JSON data + template
