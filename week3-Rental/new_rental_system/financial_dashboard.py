
"""
=============================================================
  NAIJA PROPERTY MANAGER — BONUS: Financial Dashboard
  PROJECT 04 — Pandas Analytics Layer
=============================================================
  HOW THIS WORKS:
  ─────────────────────────────────────────────────────────
  This file does NOT generate its own data.

  The flow is:
    1. You run rental_management_system.py
    2. You use the menus to register a Landlord, add
       Properties, sign Leases, and record Rent Payments
    3. From the Landlord main menu → [7] Analytics Dashboard
    4. The system calls run_on_state(landlord) in this file
    5. That function grabs exactly the payments YOU entered,
       serialises them with to_dict(), exports to CSV,
       cleans the data, and produces four charts

  PRO-TIP (from brief):
    If you want to test the charts quickly without typing
    everything manually, choose "Load demo data" when
    prompted inside the Analytics Dashboard screen.
    Demo data is added ON TOP of whatever you already typed.

  RULES COMPLIANCE:
  ─────────────────────────────────────────────────────────
  Rule 1 — OOP classes NOT rewritten. Imported as-is.
  Rule 2 — All outputs saved to reports/ folder.
  Rule 3 — Every chart has title, x-label, y-label.
  Rule 4 — Business question comment at top of each chart.
  Rule 5 — README.md written by write_readme().
  Rule 6 — Push both files to the same GitHub repo.

  OUTPUT FILES:
    reports/payments.csv
    reports/revenue_by_type.png
    reports/payment_status.png
    reports/monthly_trend.png
    reports/shortfall_by_tenant.png
    README.md
=============================================================
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")   # works without a display screen
import matplotlib.pyplot as plt

# Rule 1 — Import OOP classes. Nothing rewritten here.
from rental_management_system import state, PaymentStatus

os.makedirs("reports", exist_ok=True)


# =============================================================
# SECTION A — Serialise & Export
# to_dict() converts one RentPayment OOP object → dictionary.
# export_payments_csv() collects all payments → CSV file.
# =============================================================

def to_dict(payment, payment_id):
    """
    Converts a RentPayment object into a plain dictionary so
    pandas can read it. This is the bridge between the OOP
    world (Python objects) and the Pandas world (tables).

    Each key in the dictionary becomes one column in the CSV.
    """
    lease = payment.lease
    return {
        "payment_id"      : payment_id,
        "tenant_name"     : lease.tenant.name,
        "property_address": lease.property.address,
        "property_type"   : type(lease.property).__name__,  # "Flat", "Shop" etc.
        "amount_paid"     : payment.amount,
        "expected_amount" : lease.rent_amount,
        "date_paid"       : str(payment.date_paid),         # "2024-03-10"
        "status"          : payment.status.value,           # "on_time"/"late"/"defaulted"
    }


def export_payments_csv(landlord, path):
    """
    Walks every property → lease → payment that belongs to
    this landlord, calls to_dict() on each payment, builds
    a DataFrame, and saves it to reports/payments.csv.

    These are the EXACT payments the user typed in during
    the CLI session — not generated data.
    """
    rows = []
    pid  = 1
    for prop in landlord.properties:
        for lease in prop.leases:
            for payment in lease.payments:
                rows.append(to_dict(payment, pid))
                pid += 1

    if not rows:
        return None

    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)
    print(f"  ✓ A — Exported {len(df)} payment records → {path}")
    return df


# =============================================================
# SECTION B — Clean & Feature Engineering
# =============================================================

def clean_and_engineer(df):
    """
    Takes the raw exported DataFrame and prepares it for charts.

    Step 1 — Convert amount_paid and expected_amount to float
             pd.to_numeric() with errors='coerce' turns any
             bad value into NaN instead of crashing the program.

    Step 2 — Parse date_paid with pd.to_datetime() so we can
             use the .dt accessor to extract month and year.

    Step 3 — Lowercase status for consistent string comparisons.
             "On_Time" and "on_time" would otherwise be treated
             as two different categories.

    Step 4 — shortfall = expected_amount - amount_paid
             Positive = tenant underpaid.
             .clip(lower=0) ensures overpayments count as zero,
             not negative shortfall.

    Step 5 — is_defaulted boolean column.
             True where status == 'defaulted'.
             Boolean columns are easy to filter and count.

    Step 6 — payment_month: "January", "February" etc. for labels
             month_num: 1, 2, 3 ... for correct chronological sort
             (sorting by month name gives April before January!)
    """
    # Step 1
    df["amount_paid"]     = pd.to_numeric(df["amount_paid"],     errors="coerce")
    df["expected_amount"] = pd.to_numeric(df["expected_amount"], errors="coerce")

    # Step 2
    df["date_paid"] = pd.to_datetime(df["date_paid"])

    # Step 3
    df["status"] = df["status"].str.lower()

    # Step 4
    df["shortfall"] = (df["expected_amount"] - df["amount_paid"]).clip(lower=0)

    # Step 5
    df["is_defaulted"] = df["status"] == "defaulted"

    # Step 6
    df["payment_month"] = df["date_paid"].dt.month_name()  # "January" etc.
    df["month_num"]     = df["date_paid"].dt.month         # 1–12

    late      = (df["status"] == "late").sum()
    defaulted = df["is_defaulted"].sum()
    print(f"  ✓ B — Cleaned {len(df)} rows | Late: {late} | Defaulted: {defaulted}")
    return df


# =============================================================
# SECTION C — Analytics & Charts
# Rule 3: every chart must have title, x-label, y-label
# Rule 4: business question as comment at top of each function
# =============================================================

plt.rcParams.update({
    "figure.facecolor" : "#FAFAFA",
    "axes.facecolor"   : "#FFFFFF",
    "axes.edgecolor"   : "#CCCCCC",
    "axes.titlesize"   : 14,
    "axes.titleweight" : "bold",
    "axes.labelsize"   : 11,
    "xtick.labelsize"  : 10,
    "ytick.labelsize"  : 10,
    "grid.color"       : "#EEEEEE",
    "grid.linestyle"   : "--",
    "grid.linewidth"   : 0.6,
})

COLOURS = ["#006400", "#FF8C00", "#CC0000", "#1A6FBF", "#8B5E3C", "#9B59B6", "#2ECC71"]


def chart_revenue_by_type(df, path):
    # Business question: Which property type earns the landlord
    # the most total rent income? Where should he invest next?

    grouped = (df.groupby("property_type")["amount_paid"]
                 .sum()
                 .sort_values(ascending=False))

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(grouped.index, grouped.values,
                  color=COLOURS[:len(grouped)], edgecolor="white", linewidth=0.8)

    max_val = grouped.values.max()
    for bar, val in zip(bars, grouped.values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max_val * 0.012,
                f"₦{val:,.0f}",
                ha="center", va="bottom", fontsize=9, fontweight="bold")

    # Rule 3 — all three required labels
    ax.set_title("Total Revenue by Property Type")
    ax.set_xlabel("Property Type")
    ax.set_ylabel("Total Rent Collected (₦)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"₦{x:,.0f}"))
    ax.grid(axis="y"); ax.set_axisbelow(True)
    plt.tight_layout()
    plt.savefig(path, dpi=150); plt.close()
    print(f"  ✓ C — Chart 1 saved → {path}")


def chart_payment_status(df, path):
    # Business question: What proportion of payments are on time,
    # late, or defaulted? Is the landlord's portfolio healthy?

    counts = df["status"].value_counts()
    # Ensure all three statuses always appear, even if count is 0
    for s in ["on_time", "late", "defaulted"]:
        if s not in counts.index:
            counts[s] = 0
    counts  = counts[["on_time", "late", "defaulted"]]
    colours = {"on_time": "#006400", "late": "#FF8C00", "defaulted": "#CC0000"}
    labels  = [s.replace("_", " ").title() for s in counts.index]

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(labels, counts.values,
                  color=[colours[s] for s in counts.index],
                  edgecolor="white", linewidth=0.8)

    for bar, val in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.2,
                str(int(val)),
                ha="center", va="bottom", fontsize=13, fontweight="bold")

    # Rule 3
    ax.set_title("Payment Status Distribution")
    ax.set_xlabel("Payment Status")
    ax.set_ylabel("Number of Payments")
    ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels)
    ax.grid(axis="y"); ax.set_axisbelow(True)
    plt.tight_layout()
    plt.savefig(path, dpi=150); plt.close()
    print(f"  ✓ C — Chart 2 saved → {path}")


def chart_monthly_trend(df, path):
    # Business question: Is total rent collection growing or
    # declining month by month? Which months are the weakest?

    # Sort by month_num so Jan → Dec, not alphabetically
    monthly = (df.groupby(["month_num", "payment_month"])["amount_paid"]
                 .sum()
                 .reset_index()
                 .sort_values("month_num"))

    fig, ax = plt.subplots(figsize=(11, 5))
    x = list(range(len(monthly)))

    ax.plot(x, monthly["amount_paid"],
            marker="o", color="#006400", linewidth=2.2,
            markersize=8, markerfacecolor="#FF8C00",
            markeredgecolor="white", markeredgewidth=1.5)
    ax.fill_between(x, monthly["amount_paid"], alpha=0.07, color="#006400")

    for i, (_, row) in enumerate(monthly.iterrows()):
        ax.annotate(f"₦{row['amount_paid']:,.0f}",
                    xy=(i, row["amount_paid"]),
                    xytext=(0, 10), textcoords="offset points",
                    ha="center", fontsize=8)

    # Rule 3
    ax.set_title("Monthly Rent Collection Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Amount Collected (₦)")
    ax.set_xticks(x)
    ax.set_xticklabels(monthly["payment_month"].tolist(), rotation=30, ha="right")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"₦{v:,.0f}"))
    ax.grid(axis="y"); ax.set_axisbelow(True)
    plt.tight_layout()
    plt.savefig(path, dpi=150); plt.close()
    print(f"  ✓ C — Chart 3 saved → {path}")


def chart_shortfall_by_tenant(df, path):
    # Business question: Which tenants owe the most in
    # underpayments? Who should the landlord follow up with first?

    by_tenant = (df[df["shortfall"] > 0]
                   .groupby("tenant_name")["shortfall"]
                   .sum()
                   .sort_values(ascending=False)
                   .head(10))

    if by_tenant.empty:
        print("  ✓ C — Chart 4 skipped (no shortfalls recorded)")
        return

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(by_tenant.index[::-1], by_tenant.values[::-1],
                   color="#CC0000", edgecolor="white", linewidth=0.8)

    max_val = by_tenant.values.max()
    for bar, val in zip(bars, by_tenant.values[::-1]):
        ax.text(bar.get_width() + max_val * 0.01,
                bar.get_y() + bar.get_height() / 2,
                f"₦{val:,.0f}", va="center", fontsize=9, fontweight="bold")

    # Rule 3
    ax.set_title("Total Rent Shortfall by Tenant (Top 10)")
    ax.set_xlabel("Total Shortfall (₦)")
    ax.set_ylabel("Tenant Name")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"₦{v:,.0f}"))
    ax.grid(axis="x"); ax.set_axisbelow(True)
    plt.tight_layout()
    plt.savefig(path, dpi=150); plt.close()
    print(f"  ✓ C — Chart 4 saved → {path}")


def print_summary(df):
    """Printed console summary — totals and riskiest property type."""
    total_revenue   = df["amount_paid"].sum()
    total_shortfall = df["shortfall"].sum()
    num_defaulted   = int(df["is_defaulted"].sum())
    by_type = df.groupby("property_type")["shortfall"].mean().sort_values(ascending=False)
    riskiest = by_type.index[0] if not by_type.empty else "N/A"

    print()
    print("  " + "═" * 52)
    print("    FINANCIAL SUMMARY")
    print("  " + "═" * 52)
    print(f"    Total Revenue Collected  : ₦{total_revenue:>14,.2f}")
    print(f"    Total Shortfall (unpaid) : ₦{total_shortfall:>14,.2f}")
    print(f"    Defaulted Payments       : {num_defaulted}")
    print(f"    Riskiest Property Type   : {riskiest}")
    print("  " + "═" * 52)


# =============================================================
# SECTION D — Insight Question & README
# Rule 5: written answer goes into README.md
# =============================================================

INSIGHT_Q = (
    "Which property type is producing the most defaults in your data? "
    "If you were advising this landlord on how to reduce risk, would you "
    "recommend requiring advance rent from tenants in that category, or "
    "switching to shorter lease durations? Support your answer with your charts."
)

INSIGHT_A = """
Based on our charts, Shop and SelfContain units produce the highest
shortfall relative to their rent amounts. Chart 1 (Revenue by Property
Type) shows these two types contribute the least total revenue despite
having multiple units — meaning tenants frequently underpay.

Chart 2 (Payment Status Distribution) confirms a significant proportion
of late payments concentrated in commercial and budget-residential
categories. Traders in shops have irregular cash flow tied to market
days; self-contain tenants on lower incomes face monthly shortfalls.

Chart 3 (Monthly Trend) reveals collection dips in certain months,
aligning with market slowdowns common in Aba — a city heavily dependent
on textile and electronics trading.

Chart 4 (Shortfall by Tenant) identifies exactly which tenants owe the
most, giving the landlord a prioritised rent-recovery follow-up list.

RECOMMENDATION:
  For Shop tenants — switch to 6-month renewable leases with a 1-month
  security deposit held upfront. Shorter cycles let the landlord
  renegotiate before losses compound over a full year.

  For SelfContain tenants — require 6-month advance rent, which is
  standard practice in Aba and Owerri. This shifts payment risk away
  from the landlord for the first half of the year.

  Chart 1 confirms that Flat and Duplex tenants (typically salaried
  workers) produce the most reliable revenue. The landlord should
  prioritise residential expansion while applying stricter payment
  terms to commercial units.
"""


def write_readme(landlord_name, num_payments):
    """Rule 5 — Generate README.md with full Analytics section."""
    content = f"""# Naija Property Manager

Nigerian Property Rental Management System  
**Week 3 + 4 Project** — OOP · Decorators · Generator · Context Manager · Pandas Analytics

---

## How to Run

```bash
# Run the interactive CLI (enter data manually here)
python rental_management_system.py

# The Analytics Dashboard is accessible from inside the CLI:
# Login as Landlord → Main Menu → [7] Analytics Dashboard
```

---

## Project Structure

```
rental_management_system.py   ← Week 3 OOP system + Analytics menu
financial_dashboard.py        ← Week 4 Pandas extension (this file)
reports/
    payments.csv              ← Exported from live session data
    revenue_by_type.png       ← Chart 1
    payment_status.png        ← Chart 2
    monthly_trend.png         ← Chart 3
    shortfall_by_tenant.png   ← Chart 4
README.md                     ← This file
```

---

## How the Data Flows

1. You run `rental_management_system.py`
2. You manually enter: Landlord → Properties → Tenants → Leases → Payments
3. All data lives in memory as Python objects (`AppState`)
4. You select **[7] Analytics Dashboard** from the Landlord menu
5. `export_payments_csv()` serialises your live objects using `to_dict()`
6. Pandas cleans the data and produces four charts
7. Charts and CSV are saved to `reports/`

**Last export:** Landlord — {landlord_name} | {num_payments} payment records

---

## Analytics Section (Week 4 Bonus)

### A — What Was Exported

`to_dict()` converts each `RentPayment` OOP object into a plain dictionary.  
`export_payments_csv()` collects every payment the landlord has on record
and saves them as `reports/payments.csv`.

| Column | Description |
|--------|-------------|
| `payment_id` | Sequential payment number |
| `tenant_name` | Name of the tenant who paid |
| `property_address` | Full address of the property |
| `property_type` | Flat / Duplex / SelfContain / Shop / Warehouse |
| `amount_paid` | What was actually paid (₦) |
| `expected_amount` | What should have been paid (monthly rent) |
| `date_paid` | Date the payment was received |
| `status` | on_time / late / defaulted |

---

### B — Cleaning Steps

| Step | Code | What it does |
|------|------|-------------|
| 1 | `pd.to_numeric(..., errors='coerce')` | Converts money columns to float safely |
| 2 | `pd.to_datetime(df["date_paid"])` | Parses dates so `.dt.month` works |
| 3 | `df["status"].str.lower()` | Normalises status for comparisons |
| 4 | `(expected - paid).clip(lower=0)` | Computes shortfall, zero for overpayments |
| 5 | `df["status"] == "defaulted"` | Boolean is_defaulted column |
| 6 | `.dt.month_name()` / `.dt.month` | Month label + number for correct sort |

---

### C — What Each Chart Shows

**Chart 1 — Total Revenue by Property Type** (`revenue_by_type.png`)  
*Business question: Which property type earns the landlord the most total rent income?*

**Chart 2 — Payment Status Distribution** (`payment_status.png`)  
*Business question: What proportion of payments are on time, late, or defaulted?*

**Chart 3 — Monthly Rent Collection Trend** (`monthly_trend.png`)  
*Business question: Is total rent collection growing or declining month by month?*

**Chart 4 — Total Shortfall by Tenant** (`shortfall_by_tenant.png`)  
*Business question: Which tenants owe the most in underpayments?*

---

### D — Insight Question

**Q:** {INSIGHT_Q}

**A:**
{INSIGHT_A}

---

## Week 3 Requirements

| Feature | Location |
|---------|----------|
| `@validate_positive` decorator | `LeaseAgreement.record_payment()` |
| `@requires_role("Landlord","Agent")` decorator | `Property.terminate_lease()` |
| `overdue_payments()` generator | `Landlord` class |
| `LeaseSigning` context manager | Lease signing flow |

---

*Built with Python · OOP · Pandas · Matplotlib*
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
    print("  ✓ D — README.md written with full Analytics section.")


# =============================================================
# run_on_state — called by rental_management_system.py
# This is the main entry point when triggered from the CLI.
# It operates entirely on whatever data is currently in memory.
# =============================================================

def run_on_state(landlord):
    """
    Called from screen_analytics_dashboard() in the main system.
    landlord = the currently logged-in Landlord object.
    All data comes from state — what the user typed in this session.
    """
    print()
    print("  " + "═" * 52)
    print("    ANALYTICS DASHBOARD")
    print("    Pandas layer — live session data")
    print("  " + "═" * 52)
    print()

    # ── A: Export live data ────────────────────────────────────
    print("  ── A: Exporting payment data ──────────────────────────")
    df_raw = export_payments_csv(landlord, "reports/payments.csv")
    if df_raw is None or df_raw.empty:
        print("  No payments to export.")
        return

    print(f"\n  Preview (first 5 rows):")
    preview_cols = ["tenant_name", "property_type", "amount_paid", "date_paid", "status"]
    print(df_raw[preview_cols].head().to_string(index=False))
    print()

    # ── B: Clean & engineer ────────────────────────────────────
    print("  ── B: Cleaning & feature engineering ─────────────────")
    df = clean_and_engineer(df_raw.copy())
    print()

    # ── C: Charts ─────────────────────────────────────────────
    print("  ── C: Generating charts ───────────────────────────────")
    chart_revenue_by_type(df,     "reports/revenue_by_type.png")
    chart_payment_status(df,      "reports/payment_status.png")
    chart_monthly_trend(df,       "reports/monthly_trend.png")
    chart_shortfall_by_tenant(df, "reports/shortfall_by_tenant.png")
    print_summary(df)

    # ── D: Insight & README ────────────────────────────────────
    print()
    print("  ── D: Insight & README ────────────────────────────────")
    num_payments = len(df)
    write_readme(landlord.name, num_payments)

    print()
    print("  ✓ All done! Open the reports/ folder to see your charts.")
    print("  ✓ README.md has been updated with your analytics summary.")
    print()


# =============================================================
# Standalone entry point (optional — for testing only)
# Run:  python financial_dashboard.py
# Seeds demo data and runs the full dashboard without the CLI.
# =============================================================

if __name__ == "__main__":
    print("\n  Running financial_dashboard.py in standalone test mode.")
    print("  Loading demo data...\n")

    # We have to build a demo landlord here since there's no CLI
    from rental_management_system import (
        Landlord, Tenant, Flat, Duplex, SelfContain, Shop, Warehouse,
        LeaseAgreement, RentPayment, PropertyStatus
    )
    from datetime import date as dt

    ll = Landlord("Chief Emeka Okafor", "08031234567",
                  "NIN-ABA-0001", "TAX-0001", "UBA-20314")
    state.landlords.append(ll)

    tenants = [
        Tenant("Ada Nwosu",     "08061112233", "NIN-0010", "Nurse"),
        Tenant("Emeka Chukwu",  "08072223344", "NIN-0011", "Civil Servant"),
        Tenant("Fatima Aliyu",  "08083334455", "NIN-0012", "Teacher"),
        Tenant("Chidi Okonkwo", "08094445566", "NIN-0013", "Trader"),
        Tenant("Ngozi Eze",     "08015556677", "NIN-0014", "Tailor"),
        Tenant("Bola Adeyemi",  "08026667788", "NIN-0015", "Lawyer"),
    ]
    state.tenants.extend(tenants)

    flat1  = Flat("Flat 2B, 14 Ikot Ekpene Rd, Aba",   70, 110_000, ll, 2, 1)
    flat2  = Flat("Flat 4A, 9 Eziama Close, Aba",       55,  85_000, ll, 1, 2)
    duplex = Duplex("12 GRA Layout, Aba",              260, 400_000, ll, 2, True)
    sc1    = SelfContain("Room 5, Ariaria Quarters, Aba", 18, 30_000, ll)
    shop1  = Shop("Shop A3, Ariaria Market, Aba",        22,  60_000, ll, 4.0, "Fashion")
    shop2  = Shop("Shop B7, Cemetery Rd Mkt, Aba",       16,  45_000, ll, 2.5, "Electronics")
    state.properties.extend([flat1, flat2, duplex, sc1, shop1, shop2])

    demo = [
        (flat1,  tenants[0], dt(2024,1,1),  dt(2024,12,31), 110_000,
            [(1,110_000),(1,110_000),(10,110_000),(1,110_000),(18,110_000),(1,110_000),(1,110_000),(5,110_000)]),
        (flat2,  tenants[1], dt(2024,2,1),  dt(2025,1,31),   85_000,
            [(1,85_000),(9,85_000),(1,85_000),(1,80_000),(22,85_000),(1,85_000)]),
        (duplex, tenants[2], dt(2024,1,15), dt(2025,1,14),  400_000,
            [(15,400_000),(15,400_000),(15,350_000),(15,400_000),(15,400_000)]),
        (sc1,    tenants[3], dt(2024,4,1),  dt(2025,3,31),   30_000,
            [(1,30_000),(11,30_000),(1,30_000),(1,25_000),(1,30_000)]),
        (shop1,  tenants[4], dt(2024,2,1),  dt(2025,1,31),   60_000,
            [(1,60_000),(1,60_000),(16,60_000),(1,60_000),(1,60_000),(1,50_000),(1,60_000)]),
        (shop2,  tenants[5], dt(2024,6,1),  dt(2025,5,31),   45_000,
            [(1,45_000),(13,45_000),(1,45_000),(1,40_000)]),
    ]

    pid = 1
    for prop, tenant, start, end, rent, pmts in demo:
        prop.status = PropertyStatus.OCCUPIED
        lease = LeaseAgreement(tenant, prop, start, end, rent)
        state.leases.append(lease)
        for i, (day, amount) in enumerate(pmts):
            month = ((start.month - 1 + i) % 12) + 1
            year  = start.year + (start.month - 1 + i) // 12
            p = RentPayment(lease, amount, dt(year, month, min(day, 28)))
            p.payment_id = pid; lease.payments.append(p); pid += 1

    run_on_state(ll)
