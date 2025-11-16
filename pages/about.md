# About: The Accountability Dashboard

## The Problem We're Solving

Political discourse has become theatre. Politicians make announcements, claim victories, and blame predecessors—while citizens struggle to know if things are actually getting better or worse.

The metrics that matter—can you afford housing, food, and healthcare—get buried under spin, complex statistics, and carefully-framed narratives. Official reports are released months late, use methodology most people can't verify, and provide politicians with endless opportunities to cherry-pick favourable numbers.

**We deserve better.** Citizens should be able to answer simple questions with hard facts:
- Is my cost of living going up or down?
- Is crime in my area getting better or worse?
- Can young people afford to buy homes?
- Is the current government improving things or not?

This dashboard exists to make those answers impossible to spin.

---

## What This Is

**The Accountability Dashboard is a public, transparent, and tamper-proof scorecard for government performance.**

It tracks objective indicators—housing costs, crime rates, healthcare wait times, education completion, and the cost of essential goods—and evaluates whether they're improving or declining.

Every metric is:
- **Independently collected** (not by the government being evaluated)
- **Publicly verifiable** (raw data, receipts, and sources published)
- **Historically preserved** (can't be revised or deleted)
- **Simply presented** (traffic light RAG scores: Red, Amber, Green)

No spin. No excuses. Just: did things get better or worse?

---

## Core Principles

### 1. **The Scorecard Doesn't Lie**

Metrics are measured year-on-year. If housing affordability was 32% and is now 28%, it got worse. The government in power owns that result.

Politicians can explain *why* (global recession, pandemic, etc.), but the official scorecard shows one thing: **did the number move in the right direction?**

Citizens decide at the ballot box whether the explanation is valid.

### 2. **Hard Numbers Beat Narrative**

We track things you can't argue with:
- The Essentials Basket (milk, bread, diesel, eggs, rice) costs what it costs. We publish the receipts.
- Crime rates are what they are. Police report them.
- Hospital wait times are measured. Patients experience them.

These aren't subject to interpretation. The basket cost $14.50 last year and $16.80 this year. That's reality.

### 3. **No Gaming Allowed**

The system is designed to resist manipulation:

- **Fixed methodology**: RAG thresholds are set once and can't be changed by governments in power
- **Independent collection**: Data is collected by statutory bodies or independent auditors, not political appointees
- **Universal application**: The same 2% threshold applies to all metrics—politicians can't redefine what "good" means
- **Public verification**: All data is published with sources, dates, and geographic granularity. Anyone can check.

### 4. **Transparency Is Non-Negotiable**

Every data point is public:
- Raw CSV files downloadable by anyone
- Receipts and sources published (photos of grocery receipts, links to official stats)
- Historical data preserved permanently (GitHub version control ensures nothing is deleted)
- Calculation methodology documented and open-source

If you don't trust the numbers, **verify them yourself.**

### 5. **Context Matters, But Results Rule**

We acknowledge that external shocks (pandemics, global recessions) affect outcomes. But:

- The scorecard still counts. No pause button.
- The government's job is to manage crises and deliver results despite challenges.
- Historical comparison is available (how did this government handle a crisis vs. previous governments?), but it doesn't change your RAG score.

---

## How It Works

### Indicators vs Metrics

**Indicators** are raw data points we track:
- Essentials Basket cost: $16.20
- Housing affordability: 28% of households spending <30% of income on housing
- Crime rate: 250 violent crimes per 100k population
- Current Prime Minister: Anthony Albanese (Labor)

Indicators are just facts. No judgment.

**Metrics** are evaluations of those indicators:
- "Is cost of living under control?" → Takes Essentials Basket + CPI indicators → Compares year-on-year → Produces 🟢 Green, 🟡 Amber, or 🔴 Red

Metrics answer the questions citizens care about.

### The RAG (Red-Amber-Green) System

Every metric gets a colour based on year-on-year change:

- **🟢 Green**: Improved by >2%
- **🟡 Amber**: Changed <2% (essentially flat—maintaining performance)
- **🔴 Red**: Declined by >2%

The 2% threshold is universal and fixed. It applies to every metric, preventing politicians from moving goalposts.

### The Scorecard

At election time, citizens see:

**Current Government (3-year term):**
- 12🟢 5🟡 3🔴

**Previous Government (3-year term):**
- 8🟢 7🟡 5🔴

That's it. No spin. Did they deliver more greens than reds? Did things improve?

### Pre-Built Scenario Reports

Citizens don't need to understand statistical methodology. They just pick a question:

- "Is the economy improving?"
- "Is crime under control?"
- "Are families better off?"

The system filters to relevant indicators, applies the RAG logic, and answers: **Yes or No**, with graphs and evidence.

Reports can be filtered by:
- Government term (current, previous, specific)
- Time period (last 12 months, last 3 years)
- Region (national, Sydney, Melbourne, regional areas)

Every report gets a permanent URL. Share it. Debate it. But the facts don't change.

---

## Technical Architecture

### Design Philosophy

**Static generation, zero runtime dependencies.**

All reports are pre-generated as static HTML. No databases, no servers, no complex infrastructure. Just HTML files served fast.

This makes the system:
- **Impossible to hack** (no dynamic server to exploit)
- **Cheap to run** (free hosting on GitHub Pages)
- **Permanent** (files are files, they don't break)
- **Transparent** (view source = see everything)

### Repository Structure

```
/Australia
  jurisdiction.yaml
  /indicators
    /essentials-basket
      indicator.yaml
      data.csv
    /housing-affordability
      indicator.yaml
      data.csv
    /crime-violent
      indicator.yaml
      data.csv
    /prime-minister
      indicator.yaml
      data.csv
  /metrics
    metrics.yaml

/United-States
  jurisdiction.yaml
  /indicators
    ...
```

**Each jurisdiction is independent.** Australia has its own indicators and metrics. The US has its own. The system is universal, the implementation is local.

### Indicator Definition

Every indicator has:

**Mandatory fields:**
```yaml
id: unique-identifier
name: Human-readable name
description: What this indicator tracks
category: government | cost-of-living | housing | safety | health | education
data_type: numeric | string | structured | boolean
```

**Everything else is flexible.** An indicator can track whatever it needs.

**Simple numeric indicator (Essentials Basket):**

```yaml
id: essentials-basket
name: Essentials Basket Cost
category: cost-of-living
data_type: numeric
national_aggregation: median

basket_items:
  - 2L milk
  - 800g bread
  - 1L diesel
  - 12 eggs
  - 1kg rice

dimensions:
  - sydney-woolworths
  - sydney-coles
  - perth-woolworths
```

**data.csv:**
```csv
date,dimension,value
2024-01-07,sydney-woolworths,15.35
2024-01-07,sydney-coles,15.40
2024-01-07,perth-woolworths,16.50
```

**Rich structured indicator (Prime Minister):**

```yaml
id: prime-minister
name: Prime Minister
category: government
data_type: structured

display_fields:
  - name
  - party
  - party_color
  - election_date
```

**data.csv:**
```csv
date,dimension,name,party,party_color,election_date
2022-05-23,national,Anthony Albanese,Labor,#E13940,2022-05-21
2018-08-24,national,Scott Morrison,Liberal,#0047AB,2019-05-18
```

### Metric Definition

Metrics combine indicators and apply RAG logic.

**metrics.yaml:**

```yaml
metrics:
  - id: cost-of-living-control
    name: Is cost of living under control?
    category: cost-of-living
    indicators:
      - essentials-basket
      - cpi
    direction: lower  # lower is better
    rag_threshold: 2.0
  
  - id: housing-affordable
    name: Is housing affordable?
    category: housing
    indicators:
      - housing-affordability
    direction: higher  # higher is better
    rag_threshold: 2.0
```

### Dimensions

Dimensions are **absolute slices**, not aggregates.

For Essentials Basket:
- `sydney-woolworths` = one data point
- `perth-woolworths` = another data point
- `national` = median of all dimensions (calculated or recorded)

**You don't add dimensions together.** They're separate views of the same indicator.

To get a national figure:
- If `national_aggregation: median` → calculate median across all dimensions
- If `national_aggregation: none` → look for `dimension: national` in the CSV (recorded directly, like CPI from ABS)

### Generation Workflow

1. **Data updated** (CSV files committed to GitHub)
2. **GitHub Action triggers**
3. **Python script runs:**
   - Reads all indicator YAML + CSV files
   - Reads metrics YAML
   - Calculates year-on-year changes
   - Applies RAG logic
   - Generates all scenario reports as static HTML (via Jinja templates)
4. **Output deployed to GitHub Pages**
5. **Citizens see updated dashboard**

No runtime. No database. Just static files.

---

## Governance

### Who Controls This?

**No one controls it. That's the point.**

The system is designed to be **governed by process, not people:**

1. **Data collection**: Independent statutory bodies (like the Australian Bureau of Statistics) or audited third-party collectors. Government cannot interfere.

2. **Methodology**: Enshrined in this document and the open-source codebase. Changes require public consultation and justification. No government in power can change RAG thresholds or calculation methods.

3. **Hosting**: Open-source repository on GitHub. Anyone can fork it. Anyone can verify the code. Historical data is version-controlled and permanent.

4. **Funding**: Minimal infrastructure costs (GitHub Pages is free). Data collection funded by statutory appropriation (immune to political defunding).

### Can This Be Gamed?

We've designed against every attack vector:

**"Can government manipulate the data?"**
→ No. Independent collection, public verification, and GitHub version control make tampering visible and provable.

**"Can government change the RAG thresholds to make themselves look better?"**
→ No. Thresholds are fixed at 2% universally. Changing them requires amending this constitution (high barrier).

**"Can government claim 'external factors' to avoid accountability?"**
→ They can explain, but the scorecard still counts. Citizens judge the explanation at the ballot box.

**"Can crowdsourced data be manipulated?"**
→ We don't use crowdsourcing. All data comes from verifiable sources (receipts, official stats, audited reports).

**"What if the methodology is wrong?"**
→ It's public. Debate it, propose improvements, submit a pull request. But changes must be transparent and justified.

---

## Why This Matters

**Democracy works when citizens have facts.**

Politicians will always spin. Media will always sensationalize. But if you can pull up a dashboard and see:

- Essentials Basket: **+11.7%** 🔴
- Housing affordability: **-12%** 🔴
- Crime rate: **+8%** 🔴
- Healthcare wait times: **+15%** 🔴

...then no amount of rhetoric changes reality.

The buck stops with the leader. They own the scorecard. If they make things better, citizens see it. If they make things worse, citizens see it.

**That's accountability.**

---

## Contributing

This is an open-source project. We need:

- **Data collectors**: Help gather indicator data (receipts, stats, sources)
- **Developers**: Improve the generation scripts, templates, and dashboard
- **Statisticians**: Validate methodology and suggest improvements
- **Citizens**: Use it, share it, hold politicians accountable

Repository: [https://github.com/massyn/political-data](https://github.com/massyn/political-data)

Questions or feedback: [Contact method]

---

**Last updated:** 16 November 2025  
**Version:** 1.0