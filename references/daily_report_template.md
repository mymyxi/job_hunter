# Daily Report Template

This file documents the two-part daily report format: TOP 3 highlights followed by a compact overview table.

---

## Report Format

```markdown
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

### 🥈 2. Company — Role Title
- **Salary**: XXX | **Match Score**: XX%
- **Posted**: XXXX | **Recruiter Active**: XXXX
- **Apply Link**: full URL
- **Match Analysis**: 50 words max

### 🥉 3. Company — Role Title
- **Salary**: XXX | **Match Score**: XX%
- **Posted**: XXXX | **Recruiter Active**: XXXX
- **Apply Link**: full URL
- **Match Analysis**: 50 words max

---

## 📋 All Roles Overview

### 🔥 Internet AI Products (N roles)

| # | Company | Role | Salary | Posted | Recruiter | Match | Apply Link |
|---|---------|------|--------|--------|-----------|-------|------------|
| 1 | XXX | XXX | XXX | date | active status | XX% note | URL |

### 🤖 Embodied Intelligence (N roles)

| # | Company | Role | Salary | Posted | Recruiter | Match | Apply Link |
|---|---------|------|--------|--------|-----------|-------|------------|

### 🏛️ Enterprise AI Architect (N roles)

| # | Company | Role | Salary | Posted | Recruiter | Match | Apply Link |
|---|---------|------|--------|--------|-----------|-------|------------|
```

## Column Specifications

| Column | Description |
|--------|-------------|
| **Company** | Company name |
| **Role** | Job title |
| **Salary** | Salary range, or "Negotiable" (面议) |
| **Posted** | Relative time preferred ("1 day ago"), fallback to date ("7/22") |
| **Recruiter** | Recruiter's last active time ("Active today" > "1 day ago" > "3 days ago") |
| **Match** | Format: `XX% one-line match reason` (e.g., "90% Agent experience directly relevant") |
| **Apply Link** | Full URL, plain text, no markdown link syntax — user must be able to copy-paste |

## Key Rules

1. **URLs must be full and copy-paste friendly** — no markdown link syntax
2. **Post time**: prefer relative time ("1 day ago", "today"), fallback to date ("7/22")
3. **Recruiter activity**: always show if available ("Active today" > "1 day ago" > "within 3 days")
4. **Match score**: calculated based on keyword overlap between resume skills and JD requirements
5. **For top candidates**: use WebFetch to scrape job detail pages for post time and recruiter activity
