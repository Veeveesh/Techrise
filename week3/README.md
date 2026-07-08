# Naija Property Manager

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

**Last export:** Landlord — Chief Emeka Okafor | 35 payment records

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

**Q:** Which property type is producing the most defaults in your data? If you were advising this landlord on how to reduce risk, would you recommend requiring advance rent from tenants in that category, or switching to shorter lease durations? Support your answer with your charts.

**A:**

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
