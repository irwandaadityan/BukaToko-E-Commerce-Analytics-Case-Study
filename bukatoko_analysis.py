"""
BukaToko E-Commerce Analytics Case Study
=========================================
Questions answered:
  Q1. Which country has the most active users in Q2 2025?
  Q2. Monthly Active User trend per channel
  Q3. Which device is used most often (by session)?
  Q4. % of users who search and then add-to-cart on the same day
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.gridspec as gridspec
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# 0. LOAD DATA
# ─────────────────────────────────────────────
FILE = "Copy_of_Dataset_Case_Study.xlsx"   # put file in same directory, or change path

df = pd.read_excel(FILE, parse_dates=["event_timestamp"])
df["date"]    = df["event_timestamp"].dt.date
df["month"]   = df["event_timestamp"].dt.to_period("M")
df["channel"] = df["channel"].fillna("unknown")

# ─────────────────────────────────────────────
# PALETTE
# ─────────────────────────────────────────────
BRAND   = "#E8472A"          # BukaToko red
PALETTE = [
    "#E8472A", "#F4845F", "#F7B267", "#6DB8A0",
    "#4A9EBF", "#8B6FBF", "#B07CD9", "#D4A5D4"
]

# ══════════════════════════════════════════════════════════════════════════════
# Q1 – Most active country in Q2 2025
# ══════════════════════════════════════════════════════════════════════════════
q2 = df[
    (df["event_timestamp"] >= "2025-04-01") &
    (df["event_timestamp"] <  "2025-07-01")
]

# Active user = unique user_id per country
country_users = (
    q2.groupby("country")["user_id"]
      .nunique()
      .sort_values(ascending=False)
      .reset_index()
)
country_users.columns = ["country", "active_users"]
country_users["rank"] = range(1, len(country_users) + 1)

print("=" * 55)
print("Q1 – Most Active Country in Q2 2025")
print("=" * 55)
print(country_users.to_string(index=False))
print(f"\n✅ Top country: {country_users.iloc[0]['country']} "
      f"({country_users.iloc[0]['active_users']:,} active users)\n")

# ══════════════════════════════════════════════════════════════════════════════
# Q2 – Monthly Active Users per Channel
# ══════════════════════════════════════════════════════════════════════════════
mau_channel = (
    df.groupby(["month", "channel"])["user_id"]
      .nunique()
      .reset_index()
)
mau_channel.columns = ["month", "channel", "mau"]
mau_channel["month_str"] = mau_channel["month"].astype(str)

pivot_mau = mau_channel.pivot(index="month_str", columns="channel", values="mau").fillna(0)

print("=" * 55)
print("Q2 – Monthly Active Users per Channel")
print("=" * 55)
print(pivot_mau.to_string())
print()

# ══════════════════════════════════════════════════════════════════════════════
# Q3 – Device used most often by session
# ══════════════════════════════════════════════════════════════════════════════
device_sessions = (
    df.drop_duplicates(subset=["session_id"])
      .groupby("device")["session_id"]
      .count()
      .sort_values(ascending=False)
      .reset_index()
)
device_sessions.columns = ["device", "sessions"]
device_sessions["pct"] = (
    device_sessions["sessions"] / device_sessions["sessions"].sum() * 100
).round(2)

print("=" * 55)
print("Q3 – Device Usage by Session")
print("=" * 55)
print(device_sessions.to_string(index=False))
print(f"\n✅ Most used device: {device_sessions.iloc[0]['device']} "
      f"({device_sessions.iloc[0]['pct']}% of sessions)\n")

# ══════════════════════════════════════════════════════════════════════════════
# Q4 – % of users who search → add_to_cart on the SAME day
# ══════════════════════════════════════════════════════════════════════════════
search_users = (
    df[df["event_type"] == "search"][["user_id", "date", "event_timestamp"]]
      .rename(columns={"event_timestamp": "search_ts"})
)

atc_users = (
    df[df["event_type"] == "add_to_cart"][["user_id", "date", "event_timestamp"]]
      .rename(columns={"event_timestamp": "atc_ts"})
)

# Merge on user + same date, then filter atc AFTER search
merged = search_users.merge(atc_users, on=["user_id", "date"])
after  = merged[merged["atc_ts"] > merged["search_ts"]]

unique_searchers = search_users["user_id"].nunique()
converted        = after["user_id"].nunique()
conversion_rate  = converted / unique_searchers * 100

print("=" * 55)
print("Q4 – Search → Add-to-Cart Conversion (Same Day)")
print("=" * 55)
print(f"  Unique users who searched         : {unique_searchers:,}")
print(f"  Unique users who ATC after search : {converted:,}")
print(f"  Conversion rate                   : {conversion_rate:.2f}%\n")

# ══════════════════════════════════════════════════════════════════════════════
# VISUALISATIONS  (saved to bukatoko_charts.png)
# ══════════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(22, 20), facecolor="#F9F5F2")
gs  = gridspec.GridSpec(3, 2, figure=fig, hspace=0.52, wspace=0.38)

TITLE_FONT   = dict(fontsize=14, fontweight="bold", color="#1A1A2E")
LABEL_FONT   = dict(fontsize=10, color="#444")
CAPTION_FONT = dict(fontsize=8.5, color="#888", style="italic")

# ── Fig header ──────────────────────────────────────────────────────────────
fig.text(0.5, 0.975, "BukaToko Analytics Case Study",
         ha="center", va="top", fontsize=22, fontweight="bold", color=BRAND)
fig.text(0.5, 0.958, "E-Commerce Funnel & User Behaviour Insights",
         ha="center", va="top", fontsize=13, color="#555")

# ── Q1 Bar chart (top-left, full width) ─────────────────────────────────────
ax1 = fig.add_subplot(gs[0, :])
colors_q1 = [BRAND if i == 0 else PALETTE[i % len(PALETTE)]
             for i in range(len(country_users))]
bars = ax1.bar(country_users["country"], country_users["active_users"],
               color=colors_q1, edgecolor="white", linewidth=0.8, width=0.6)
for bar, val in zip(bars, country_users["active_users"]):
    ax1.text(bar.get_x() + bar.get_width() / 2,
             bar.get_height() + 8, f"{val:,}",
             ha="center", va="bottom", fontsize=10, fontweight="bold", color="#333")
ax1.set_title("Q1 · Active Users by Country — Q2 2025 (Apr–Jun)",
              **TITLE_FONT, pad=12)
ax1.set_xlabel("Country", **LABEL_FONT)
ax1.set_ylabel("Unique Active Users", **LABEL_FONT)
ax1.set_facecolor("#FAFAFA")
ax1.spines[["top", "right"]].set_visible(False)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax1.set_ylim(0, country_users["active_users"].max() * 1.18)
ax1.text(0.99, 0.97,
         f"Top: {country_users.iloc[0]['country']} "
         f"({country_users.iloc[0]['active_users']:,} users)",
         transform=ax1.transAxes, ha="right", va="top",
         fontsize=10, color=BRAND, fontweight="bold",
         bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=BRAND, alpha=0.8))

# ── Q2 Line chart (middle, full width) ──────────────────────────────────────
ax2 = fig.add_subplot(gs[1, :])
months = pivot_mau.index.tolist()
x_pos  = np.arange(len(months))
channels_sorted = pivot_mau.sum().sort_values(ascending=False).index.tolist()
for i, ch in enumerate(channels_sorted):
    color = PALETTE[i % len(PALETTE)]
    y = pivot_mau[ch].values
    ax2.plot(x_pos, y, marker="o", linewidth=2.2, markersize=6,
             color=color, label=ch)
    ax2.text(x_pos[-1] + 0.08, y[-1], ch,
             va="center", fontsize=8.5, color=color, fontweight="bold")
ax2.set_xticks(x_pos)
ax2.set_xticklabels(months, rotation=30, ha="right", fontsize=9)
ax2.set_title("Q2 · Monthly Active Users per Acquisition Channel",
              **TITLE_FONT, pad=12)
ax2.set_ylabel("Unique Active Users", **LABEL_FONT)
ax2.set_facecolor("#FAFAFA")
ax2.spines[["top", "right"]].set_visible(False)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax2.legend(loc="upper left", fontsize=8, framealpha=0.7, ncol=3)
ax2.set_xlim(-0.3, len(months) - 0.3)

# ── Q3 Donut (bottom-left) ───────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[2, 0])
wedges, texts, autotexts = ax3.pie(
    device_sessions["sessions"],
    labels=device_sessions["device"],
    autopct="%1.1f%%",
    colors=[PALETTE[i] for i in range(len(device_sessions))],
    startangle=90,
    wedgeprops=dict(width=0.55, edgecolor="white", linewidth=2),
    pctdistance=0.78
)
for t in texts:
    t.set_fontsize(11)
    t.set_fontweight("bold")
for at in autotexts:
    at.set_fontsize(10)
    at.set_color("white")
    at.set_fontweight("bold")
ax3.set_title("Q3 · Device Usage by Session",
              **TITLE_FONT, pad=12)
centre = plt.Circle((0, 0), 0.45, fc="#F9F5F2")
ax3.add_artist(centre)
top_dev = device_sessions.iloc[0]
ax3.text(0, 0.12, top_dev["device"].upper(), ha="center",
         fontsize=11, fontweight="bold", color=BRAND)
ax3.text(0, -0.12, f"{top_dev['pct']:.1f}%", ha="center",
         fontsize=13, fontweight="bold", color="#1A1A2E")

# ── Q4 Funnel / Bar (bottom-right) ──────────────────────────────────────────
ax4 = fig.add_subplot(gs[2, 1])
funnel_labels = ["Searched\n(unique users)", "ATC after\nSearch (same day)"]
funnel_vals   = [unique_searchers, converted]
funnel_colors = [PALETTE[4], BRAND]
h_bars = ax4.barh(funnel_labels[::-1], funnel_vals[::-1],
                   color=funnel_colors[::-1], edgecolor="white",
                   linewidth=0.8, height=0.45)
for bar, val in zip(h_bars, funnel_vals[::-1]):
    ax4.text(val + unique_searchers * 0.01, bar.get_y() + bar.get_height() / 2,
             f"{val:,}", va="center", fontsize=11, fontweight="bold", color="#333")
ax4.set_xlim(0, unique_searchers * 1.25)
ax4.set_facecolor("#FAFAFA")
ax4.spines[["top", "right"]].set_visible(False)
ax4.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax4.set_title("Q4 · Search → Add-to-Cart Conversion (Same Day)",
              **TITLE_FONT, pad=12)
ax4.set_xlabel("Users", **LABEL_FONT)
ax4.text(0.97, 0.08,
         f"Conversion Rate\n{conversion_rate:.2f}%",
         transform=ax4.transAxes, ha="right", va="bottom",
         fontsize=14, fontweight="bold", color=BRAND,
         bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=BRAND, alpha=0.9))

# ── Save ────────────────────────────────────────────────────────────────────
OUT = "bukatoko_charts.png"
plt.savefig(OUT, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.show()
print(f"\n📊 Charts saved to: {OUT}")
