---
name: audit-web
description: >
  Audits a web project (technical, SEO, UX/UI, security) from a Jira or Trello ticket —
  or, failing that, a free-text description — following a 5-step methodology (scoping,
  data collection, diagnosis, synthesis, action plan). Produces a presentation artifact
  that explains each step and what remains to be done, with a man-day estimate and the
  equivalent Claude Code time for every task.
  Use for "web audit", "audit the site", "audit ticket X", "audit grid",
  "man-day estimate for an audit", "audit web", "audite le site".
argument-hint: "[Jira key / Trello URL / ticket description]"
---

# Web Audit — 5-step grid, estimated in man-days

Two resources support this skill — read them when you reach the relevant step:

- `references/methodology.md` — the 5 steps in detail, the task list T1.1 → T5.4 with
  baseline estimates, and a sample roadmap (quick wins / mid-term / major overhaul)
- `assets/audit-web-grid.html` — the visual template for the final artifact (masthead,
  navigation rail, task tables, comparison, roadmap, "remaining work" checklist), light
  and dark

## 0. Fetch the ticket

From `$ARGUMENTS`:

- **Jira key** (`[A-Z]+-[0-9]+` or a `browse/` URL) → read the ticket through the
  Atlassian MCP (`getJiraIssue`, markdown format, with description and comments)
- **Trello URL** → read the card through the Trello MCP if available
- **Free text** → use it as-is as the description

If nothing is provided, or the connector is unavailable, ask for the ticket description.
If the site type (showcase, e-commerce, SaaS) or the main problem cannot be inferred,
ask those two questions before continuing.

## 1. Scope

Extract from the ticket: the **trigger** (traffic drop, redesign, slowness, conversion,
security), the **scope** (full or targeted: SEO, performance, accessibility, e-commerce,
UX), the constraints and the expected deliverables. Anything out of scope leaves the grid.

## 2. Build the task grid

Start from the baseline list in `references/methodology.md` and **tailor it to the
ticket**:

- drop out-of-scope tasks (e.g. no T3.2 SEO for a security-only audit)
- add context-specific tasks (e.g. checkout funnel for an e-commerce site)
- adjust estimates to the size of the site and to what is already done
- mark as "human only" the tasks that need third-party tool access or someone in the
  room (heatmaps, oral presentation)

For each task: ID, description, man-days, Claude Code time, and status
(**done / in progress / to do**) based on what the ticket says.

## 3. Produce the artifact

Load the `artifact-design` skill, then start from `assets/audit-web-grid.html`:

- fill in the masthead (site type, trigger, scope, ticket reference)
- one section per step with its task table and subtotal
- the man-days vs Claude Code comparison (recomputed totals)
- the prioritised roadmap: quick wins / mid-term / major overhaul
- the "remaining work" checklist, fed by unfinished tasks

Publish with the Artifact tool and share the link.

## Rules

- Claude Code estimates assume human review: never present them as unsupervised time.
  Keep the template's table footnote.
- Recompute subtotals and totals after every adjustment — never copy figures from the
  template.
- Write in the language of the ticket.
