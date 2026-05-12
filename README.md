# 🛒 BukaToko E-Commerce Analytics Case Study

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.7+-11557C?style=for-the-badge&logo=python&logoColor=white)
![Status](https://img.shields.io/badge/Status-Complete-E8472A?style=for-the-badge)

**Exploratory data analysis of a Southeast Asia e-commerce platform — uncovering user behaviour, funnel drop-offs, and channel performance across 10,000 events.**

</div>

---

## Context

**BukaToko** is a fictional online e-commerce platform operating across Southeast Asia, the US, and Australia. Users browse products, search, add to cart, and purchase via web and mobile app. The marketing team attracts users through organic search, paid ads, email, social media, referrals, and direct visits.

As the analytics team, the goal was to **explore user behaviour and improve funnel conversion** using real event-level data.

---

## Dataset

| Column | Description |
|---|---|
| `event_id` | Unique identifier for each event (UUID) |
| `user_id` | Unique identifier for each user (UUID) |
| `session_id` | Session identifier — multiple events per session |
| `event_type` | `page_view`, `product_view`, `search`, `add_to_cart`, `checkout`, `purchase`, `login`, `logout` |
| `event_timestamp` | Date and time of the event |
| `product_id` | Product interacted with (NaN for non-product events) |
| `country` | User's country code (`ID`, `US`, `SG`, etc.) |
| `device` | `desktop`, `IOS`, `android` |
| `channel` | `organic`, `paid_search`, `email`, `referral`, `social`, `direct` |

- **Rows:** 10,000 events
- **Date range:** March – September 2025
- **Countries:** ID, US, AU, VN, PH, SG, MY, TH

---

## Questions Answered

### Q1 · Which country has the most active users in Q2 2025?

**Active user** = unique `user_id` with at least one event between April 1 – June 30, 2025.

```python
q2 = df[
    (df["event_timestamp"] >= "2025-04-01") &
    (df["event_timestamp"] <  "2025-07-01")
]

country_users = (
    q2.groupby("country")["user_id"]
      .nunique()
      .sort_values(ascending=False)
      .reset_index()
)
```

**Result:**

| Rank | Country | Active Users |
|------|---------|-------------|
| 1 | **ID** (Indonesia) | **1,055** |
| 2 | US | 815 |
| 3 | VN | 485 |
| 4 | PH | 464 |
| 5 | MY | 460 |
| 6 | SG | 459 |
| 7 | TH | 236 |
| 8 | AU | 215 |

> Indonesia leads by **29% over the US**, making it the core market for growth investment.

---

### Q2 · Monthly Active User trend per channel

```python
mau_channel = (
    df.groupby(["month", "channel"])["user_id"]
      .nunique()
      .reset_index()
)
pivot_mau = mau_channel.pivot(index="month_str", columns="channel", values="mau").fillna(0)
```

**Result:**

| Month | Direct | Email | Organic | Paid Search | Referral | Social |
|-------|--------|-------|---------|-------------|----------|--------|
| 2025-03 | 41 | 33 | 34 | 38 | 50 | 40 |
| 2025-04 | 262 | 258 | 260 | 255 | 244 | 276 |
| 2025-05 | 270 | 284 | 251 | 259 | 244 | 268 |
| 2025-06 | 271 | 263 | 259 | 258 | 289 | 262 |
| 2025-07 | 257 | 290 | 268 | 288 | 255 | 250 |
| 2025-08 | 250 | 248 | 249 | 251 | 292 | 240 |
| 2025-09 | 186 | 209 | 208 | 206 | 197 | 174 |

> All channels follow the same trajectory — ramp-up in April, plateau through August, then a September drop. No single channel dominates — diversification is working, but the Sep drop warrants investigation.

---

### Q3 · Which device is used most often (by session)?

Each session is counted once by taking `drop_duplicates` on `session_id` before grouping.

```python
device_sessions = (
    df.drop_duplicates(subset=["session_id"])
      .groupby("device")["session_id"]
      .count()
      .sort_values(ascending=False)
      .reset_index()
)
```

**Result:**

| Device | Sessions | Share |
|--------|----------|-------|
| **Android** | **4,961** | **49.6%** |
| iOS | 4,000 | 40.0% |
| Desktop | 1,039 | 10.4% |

> BukaToko is a **mobile-first platform** — 89.6% of all sessions come from mobile devices. Desktop optimization should be deprioritized; Android performance and UX is critical.

---

### Q4 · What % of users who search end up adding to cart on the same day?

**Attribution rule:** The `add_to_cart` event must occur **strictly after** the `search` event, on the **same date**, and for the **same user**.

```python
search_users = (
    df[df["event_type"] == "search"][["user_id", "date", "event_timestamp"]]
      .rename(columns={"event_timestamp": "search_ts"})
)

atc_users = (
    df[df["event_type"] == "add_to_cart"][["user_id", "date", "event_timestamp"]]
      .rename(columns={"event_timestamp": "atc_ts"})
)

# Merge on same user + same date, then keep only ATC events AFTER search
merged = search_users.merge(atc_users, on=["user_id", "date"])
after  = merged[merged["atc_ts"] > merged["search_ts"]]

unique_searchers = search_users["user_id"].nunique()   # 750
converted        = after["user_id"].nunique()           # 1
conversion_rate  = converted / unique_searchers * 100  # 0.13%
```

**Result:**

```
Unique users who searched         : 750
Unique users who ATC after search :   1
Conversion rate                   : 0.13%
```

> **Critical finding:** Only **0.13%** of users who searched went on to add a product to cart on the same day. This signals a broken discovery-to-intent funnel — search results may not be relevant enough to drive cart adds. **Recommended actions:** improve search ranking algorithm, add "similar products" nudges post-search, and A/B test cart prompts.

---

## Visualisations

The script generates a 4-panel chart (`bukatoko_charts.png`) covering all four questions:

```python
fig = plt.figure(figsize=(22, 20), facecolor="#F9F5F2")
gs  = gridspec.GridSpec(3, 2, figure=fig, hspace=0.52, wspace=0.38)
```

| Panel | Chart Type | Question |
|-------|-----------|----------|
| Top (full width) | Bar chart | Q1 — Active users by country |
| Middle (full width) | Multi-line chart | Q2 — MAU trend per channel |
| Bottom-left | Donut chart | Q3 — Device share by session |
| Bottom-right | Horizontal bar | Q4 — Search → ATC funnel |

---

## How to Run

**1. Clone the repo**
```bash
git clone https://github.com/irwandaadityan/bukatoko-analytics.git
cd bukatoko-analytics
```

**2. Install dependencies**
```bash
pip install pandas matplotlib numpy openpyxl
```

**3. Place the dataset**
```
bukatoko-analytics/
├── bukatoko_analysis.py
└── Copy_of_Dataset_Case_Study.xlsx
```

**4. Run the analysis**
```bash
python bukatoko_analysis.py
```

**Output:**
- Console: printed tables for all 4 questions
- File: `bukatoko_charts.png` — 4-panel dashboard

---

## 🛠 Tech Stack

| Tool | Purpose |
|------|---------|
| `pandas` | Data loading, groupby, merging, pivoting |
| `matplotlib` | Bar, line, donut, horizontal bar charts |
| `numpy` | Axis positioning |
| `openpyxl` | Reading `.xlsx` files |

---

## File Structure

```
bukatoko-analytics/
├── bukatoko_analysis.py        # Main analysis script
├── bukatoko_charts.png         # Output chart (generated on run)
├── README.md                   # This file
└── Copy_of_Dataset_Case_Study.xlsx  # Dataset

---

## Key Insights Summary

| # | Insight | Implication |
|---|---------|-------------|
| 1 | 🇮🇩 Indonesia is the #1 market (1,055 MAU in Q2) | Double down on ID — localisation, campaigns, logistics |
| 2 |  All channels perform similarly, peaking Apr–Aug | Channel diversification is healthy; investigate Sep drop |
| 3 |  Android = 49.6% of all sessions | Prioritise Android app performance and UX |
| 4 |  Only 0.13% search→ATC conversion | Fix search relevance and add post-search cart nudges |
