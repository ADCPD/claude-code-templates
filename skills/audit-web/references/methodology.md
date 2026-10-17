# Web audit methodology

A web project audit is a complete, structured analysis of a website's current state
(technical, content, design, search and security) to identify its strengths and
blockers, and to define a corrective or strategic action plan.

It runs in 5 sequential steps. The estimates below are baselines for a mid-sized site,
to be adjusted to the ticket.

## 1. Scoping and objectives

- **Priorities**: identify why the audit is needed (traffic drop, upcoming redesign,
  slowness, conversion problem or security flaw).
- **Scope**: full or targeted audit (SEO, performance, accessibility, e-commerce, UX).

| Task | Description | Man-days | Claude Code |
| --- | --- | --- | --- |
| T1.1 | Kick-off meeting: trigger, priorities, stakeholders | 0.5 d | 0.5 h (prep material) |
| T1.2 | Define the scope — full or targeted audit | 0.25 d | 0.5 h |
| T1.3 | Write the scoping note and milestones | 0.25 d | 1 h |
| **Subtotal** | | **1.0 d** | **2 h** |

## 2. Data collection

- **Analysis tools**: crawlers, search consoles, audience measurement, behavioural
  analytics (heatmaps, session recordings).
- **Inventory**: pages, content, plugins, code and data flows.

| Task | Description | Man-days | Claude Code |
| --- | --- | --- | --- |
| T2.1 | Full site crawl (setup and run) | 0.5 d | 1.5 h |
| T2.2 | Export and review Search Console / Analytics | 0.5 d | 1 h |
| T2.3 | Heatmap / session recording analysis | 0.5 d | human — third-party tool access required |
| T2.4 | Inventory of pages, content, plugins | 0.5 d | 1 h |
| T2.5 | Inventory of code, dependencies, repository | 0.5 d | 0.75 h |
| **Subtotal** | | **2.5 d** | **4.25 h** |

## 3. Technical and thematic diagnosis

- **Technical**: HTTP errors (404, 5xx), redirects, robots.txt, XML sitemap, mobile
  compatibility, load speed.
- **SEO**: tags (title, H1), internal linking, semantic relevance, backlinks.
- **UX / UI**: navigation, readability, conversion funnels, accessibility.
- **Security**: SSL certificate, CMS/plugin updates, HTTP headers.

| Task | Description | Man-days | Claude Code |
| --- | --- | --- | --- |
| T3.1 | Technical audit — HTTP errors, redirects, robots.txt, XML sitemap, mobile, speed | 1.5 d | 3 h |
| T3.2 | SEO audit — title/H1 tags, internal linking, semantics, backlinks | 1.5 d | 3 h |
| T3.3 | UX/UI audit — navigation, readability, conversion funnels, accessibility | 1.0 d | 2 h |
| T3.4 | Security audit — SSL certificate, CMS/plugin updates, HTTP headers | 1.0 d | 2 h |
| **Subtotal** | | **5.0 d** | **10 h** |

## 4. Synthesis and cross-analysis

- Group findings to separate surface symptoms from root causes.
- Assess the impact of each issue on business objectives.

| Task | Description | Man-days | Claude Code |
| --- | --- | --- | --- |
| T4.1 | Group findings, identify root causes | 0.75 d | 1.5 h |
| T4.2 | Assess the business impact of each issue | 0.5 d | 1 h |
| **Subtotal** | | **1.25 d** | **2.5 h** |

## 5. Action plan and recommendations

- Prioritised roadmap: quick wins, mid-term projects, major overhaul.
- Detailed audit report for technical teams, the client or management.

| Task | Description | Man-days | Claude Code |
| --- | --- | --- | --- |
| T5.1 | Build the prioritised roadmap | 0.75 d | 1.5 h |
| T5.2 | Write the detailed audit report | 1.5 d | 3 h |
| T5.3 | Prepare the presentation deck | 0.5 d | 1 h |
| T5.4 | Present findings to the client | 0.5 d | human only |
| **Subtotal** | | **3.25 d** | **5.5 h** |

**Baseline total: 13 man-days · ≈ 24 h with Claude Code** (excluding human-only tasks).

## Sample roadmap

| Horizon | Example action | Estimate |
| --- | --- | --- |
| Quick wins — fast, high-impact actions | Fix duplicate title / meta tags | 0.5 d |
| | Compress oversized images | 0.5 d |
| | 301-redirect high-traffic 404s | 0.5 d |
| | Update the CMS and outdated plugins | 0.5 d |
| Mid-term — 2 to 6 weeks | Rework internal linking | 3 d |
| | Improve load times (LCP, CLS) | 4 d |
| | Rework the conversion funnel and A/B test it | 5 d |
| Major overhaul — quarter and beyond | Redesign the information architecture | 15 d |
| | Migrate to a more secure, faster CMS | 25 d |

These actions are examples: replace them with the ones coming from actual findings.
