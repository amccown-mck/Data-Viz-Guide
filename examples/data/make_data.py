"""Generate synthetic, illustrative workforce-intelligence datasets for the example gallery.

All data is fabricated (seeded) - safe to share. Covers individual, team, firm and sector levels, and mixes
internal signals (HRIS-like) with external signals (labor-market-like).

    python examples/data/make_data.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent



def attrition_by_job_family() -> pd.DataFrame:
    """Firm level, internal. Voluntary attrition by job family vs enterprise rate."""
    rows = [
        ("Pharmacy Technician", 6200, 27.4), ("Distribution Center Associate", 11800, 24.1),
        ("Customer Care", 3100, 18.9), ("Specialty Nursing", 1400, 14.2), ("Supply Chain Planning", 900, 11.8),
        ("Sales", 2300, 10.6), ("Software Engineering", 2600, 9.8), ("Data & Analytics", 850, 12.9),
        ("Finance", 1200, 7.4), ("HR", 700, 8.1),
    ]
    df = pd.DataFrame(rows, columns=["job_family", "headcount", "vol_attrition_pct"])
    df["enterprise_rate_pct"] = round(np.average(df.vol_attrition_pct, weights=df.headcount), 1)
    return df.sort_values("vol_attrition_pct", ascending=False, kind="stable")   # stable: ties keep row order


def data_ai_supply_demand() -> pd.DataFrame:
    """Firm level SWP. Forecast demand vs internal supply of Data & AI FTE."""
    years = np.arange(2024, 2031)
    demand = np.round(850 * (1.11 ** (years - 2024)))
    supply = np.round(850 * (1.035 ** (years - 2024)) - 12 * (years - 2024))
    return pd.DataFrame({"year": years, "demand_fte": demand.astype(int), "internal_supply_fte": supply.astype(int)})


def automation_exposure() -> pd.DataFrame:
    """Team/role level, internal x external. Share of task hours exposed to gen AI (external task taxonomy) vs headcount."""
    rows = [
        ("Customer Care", 3100, 58, 48), ("Claims & Billing Specialist", 1900, 63, 52), ("Finance Operations", 800, 55, 71),
        ("HR Operations", 450, 51, 62), ("Software Engineering", 2600, 41, 138), ("Data & Analytics", 850, 46, 121),
        ("Sales", 2300, 28, 96), ("Pharmacy Technician", 6200, 22, 41), ("Distribution Center Associate", 11800, 9, 39),
        ("Specialty Nursing", 1400, 14, 94), ("Supply Chain Planning", 900, 38, 88), ("Marketing", 600, 49, 92),
    ]
    return pd.DataFrame(rows, columns=["role", "headcount", "genai_exposure_pct", "median_pay_k"])


def labor_cost_bridge() -> pd.DataFrame:
    """Firm level. FY25 -> FY26 labor cost bridge ($M)."""
    rows = [("FY25 labor cost", 4210, "total"), ("Merit & market adjustments", 139, "delta"),
            ("Net new hires", 96, "delta"), ("Attrition backfill lag", -58, "delta"),
            ("Automation savings", -71, "delta"), ("Contractor conversion", -24, "delta"), ("FY26 labor cost", None, "total")]
    df = pd.DataFrame(rows, columns=["step", "value_musd", "kind"])
    df.loc[df.index[-1], "value_musd"] = df.value_musd.iloc[:-1].sum()
    return df


def mobility_flows() -> pd.DataFrame:
    """Individual -> aggregated. Internal moves between job families over 24 months."""
    flows = [
        ("Pharmacy Technician", "Specialty Pharmacy Ops", 310), ("Pharmacy Technician", "Customer Care", 140),
        ("Customer Care", "Sales", 120), ("Customer Care", "Data & Analytics", 35), ("DC Associate", "Supply Chain Planning", 180),
        ("DC Associate", "DC Leadership", 260), ("Supply Chain Planning", "Data & Analytics", 60),
        ("Sales", "Customer Success", 90), ("Customer Care", "Customer Success", 75),
    ]
    return pd.DataFrame(flows, columns=["from_family", "to_family", "moves"])


def engagement_vs_benchmark() -> pd.DataFrame:
    """Team/BU level, internal vs external benchmark. Engagement driver score minus healthcare benchmark (pts)."""
    drivers = ["Growth", "Manager support", "Recognition", "Workload", "Tools & tech", "Belonging", "Pay fairness"]
    matrix = {
        "Corporate":                 [2, 4, 1, 3, 1, 5, -1],
        "Medical-Surgical":          [-1, 3, 2, -5, 0, 6, 1],
        "Oncology & Multispecialty": [-3, 1, -2, -11, -6, 4, -4],
        "RxTS":                      [1, -2, 3, -4, 2, 3, -6],
        "Technology":                [6, 1, 4, -7, 8, 3, -3],
        "U.S. Pharmaceutical":       [-6, -4, 2, -8, -1, 5, 0],
    }
    df = pd.DataFrame(matrix, index=drivers).T.stack().reset_index()
    df.columns = ["business_unit", "driver", "delta_vs_benchmark_pts"]
    return df


def pay_vs_market() -> pd.DataFrame:
    """Role level, internal vs external. Median base pay vs external market median ($K)."""
    rows = [("Pharmacist", 138, 146), ("Pharmacy Technician", 41, 44), ("Data Scientist", 131, 128),
            ("Software Engineer", 138, 142), ("Supply Chain Planner", 88, 86), ("RN, Specialty", 94, 101),
            ("Customer Care Rep", 48, 47), ("Account Executive", 96, 94)]
    df = pd.DataFrame(rows, columns=["role", "internal_median_k", "market_median_k"])
    df["gap_pct"] = ((df.internal_median_k / df.market_median_k - 1) * 100).round(1)
    return df.sort_values("gap_pct", kind="stable")    # stable: ties (2.1, 2.3) keep row order on every platform


def skills_demand_rank() -> pd.DataFrame:
    """Sector level, external. Rank of skills in healthcare-distribution job postings, 2023 vs 2026."""
    rows = [("Inventory management", 1, 3), ("Customer service", 2, 5), ("Regulatory compliance", 3, 2),
            ("Data analysis", 4, 1), ("Automation / robotics", 5, 4), ("Clinical documentation", 6, 7),
            ("Sales & negotiation", 7, 8), ("Project management", 8, 9), ("Gen AI / prompt design", 9, 6)]
    return pd.DataFrame(rows, columns=["skill", "rank_2023", "rank_2026"])


def workforce_mix() -> pd.DataFrame:
    """Function level. Share of workforce by employment type (%), and total workers (for Marimekko widths)."""
    rows = [("Distribution", 71, 22, 7, 14200), ("Pharmacy Ops", 83, 12, 5, 9600), ("Technology", 58, 12, 30, 4100),
            ("Customer Care", 64, 30, 6, 3400), ("Corporate", 88, 4, 8, 5300)]
    return pd.DataFrame(rows, columns=["function", "employee_ft_pct", "employee_pt_pct", "contingent_pct", "workers"])


def tech_mix_by_fy() -> pd.DataFrame:
    """Function level over time. Technology workforce by employment type, FY22-FY26 (%)."""
    contingent = [18, 21, 24, 27, 30]
    pt = [10, 11, 11, 12, 12]
    return pd.DataFrame({"fiscal_year": ["FY22", "FY23", "FY24", "FY25", "FY26"],
                         "employee_ft_pct": [100 - c - p for c, p in zip(contingent, pt)],
                         "employee_pt_pct": pt, "contingent_pct": contingent})


def data_ai_gap_plan() -> pd.DataFrame:
    """Firm level SWP plan. How the Data & AI capability gap (demand - internal supply) is closed: build/buy/borrow/automate."""
    sd = data_ai_supply_demand().set_index("year")
    shares = {2026: (0.19, 0.59, 0.18, 0.04), 2028: (0.33, 0.50, 0.13, 0.04), 2030: (0.40, 0.47, 0.10, 0.03)}
    rows = []
    for yr, (build, buy, borrow, auto) in shares.items():
        gap = int(sd.demand_fte[yr] - sd.internal_supply_fte[yr])
        b, bo, a = round(gap * build), round(gap * borrow), round(gap * auto)
        rows.append((f"FY{yr % 100}", gap, b, gap - b - bo - a, bo, a))
    return pd.DataFrame(rows, columns=["fiscal_year", "gap_fte", "build_fte", "buy_fte", "borrow_fte", "automate_fte"])


def engagement_items() -> pd.DataFrame:
    """Team level, internal survey. Share of respondents unfavorable / neutral / favorable by item, Distribution (%)."""
    rows = [("I have the tools to do my job well", 31, 22, 47), ("My workload is manageable", 38, 24, 38),
            ("I see a path to grow here", 27, 25, 48), ("My manager supports my development", 14, 18, 68),
            ("I feel I belong on my team", 9, 17, 74), ("I would recommend McKesson as a place to work", 18, 23, 59)]
    return pd.DataFrame(rows, columns=["item", "unfavorable_pct", "neutral_pct", "favorable_pct"])


def headcount_bridge() -> pd.DataFrame:
    """Firm level. Headcount bridge FY25 -> FY26 for frontline job families (people)."""
    rows = [("FY25 headcount", 18000, "total"), ("External hires", 4660, "delta"), ("Internal moves in", 520, "delta"),
            ("Voluntary exits", -4543, "delta"), ("Involuntary exits", -610, "delta"), ("Internal moves out", -330, "delta"),
            ("FY26 headcount", None, "total")]
    df = pd.DataFrame(rows, columns=["step", "people", "kind"])
    df.loc[df.index[-1], "people"] = df.people.iloc[:-1].sum()
    df["people"] = df.people.astype(int)
    return df


def compa_ratio_individuals() -> pd.DataFrame:
    """Individual level, internal. Compa-ratio (base pay / range midpoint) per employee, six job families."""
    rng = np.random.default_rng(26)
    spec = [("Pharmacy Technician", 620, 0.935, 0.065), ("Distribution Center Associate", 480, 0.985, 0.05),
            ("Customer Care Rep", 210, 0.99, 0.055), ("Pharmacist", 140, 1.005, 0.045),
            ("Software Engineer", 160, 1.02, 0.06), ("Supply Chain Planner", 90, 1.01, 0.05)]
    frames = [pd.DataFrame({"job_family": fam, "compa_ratio": rng.normal(mu, sd, n).round(3)})
              for fam, n, mu, sd in spec]
    return pd.concat(frames, ignore_index=True)


def job_family_scorecard() -> pd.DataFrame:
    """Firm level, internal. One row per job family: size, attrition, hiring and engagement (FY26).
    attrition_change_pts = FY26 minus FY25 average of attrition_quarterly where that set covers the family."""
    rows = [
        ("Pharmacy Technician", 6200, 27.4, -5.6, 52, 31, 68),
        ("Distribution Center Associate", 11800, 24.1, -0.3, 24, 18, 66),
        ("Customer Care", 3100, 18.9, -0.2, 29, 22, 71),
        ("Specialty Nursing", 1400, 14.2, -0.5, 71, 26, 74),
        ("Data & Analytics", 850, 12.9, 0.4, 58, 41, 77),
        ("Supply Chain Planning", 900, 11.8, -0.3, 47, 44, 75),
        ("Sales", 2300, 10.6, -0.9, 45, 35, 76),
        ("Software Engineering", 2600, 9.8, -1.0, 49, 29, 74),
    ]
    return pd.DataFrame(rows, columns=["job_family", "headcount", "vol_attrition_pct", "attrition_change_pts",
                                       "median_days_to_fill", "internal_fill_pct", "engagement_index"])


def skills_overlap() -> pd.DataFrame:
    """Firm level, internal. Employees by combination of verified skill areas (skills inventory)."""
    rows = [(1, 0, 0, 3900), (0, 1, 0, 1250), (0, 0, 1, 2400), (1, 1, 0, 210), (0, 1, 1, 380), (1, 0, 1, 520),
            (1, 1, 1, 140)]
    return pd.DataFrame(rows, columns=["clinical", "data_analytics", "supply_chain", "employees"])


def hiring_flow_by_family() -> pd.DataFrame:
    """Firm level, internal. FY26 hires vs voluntary exits, and median days to fill FY25 vs FY26, by job family."""
    rows = [
        ("Pharmacy Technician", 6200, 27.4, 1540, 41, 52),
        ("Distribution Center Associate", 11800, 24.1, 3120, 26, 24),
        ("Customer Care", 3100, 18.9, 470, 31, 29),
        ("Specialty Nursing", 1400, 14.2, 260, 63, 71),
        ("Data & Analytics", 850, 12.9, 190, 49, 58),
        ("Supply Chain Planning", 900, 11.8, 120, 45, 47),
        ("Sales", 2300, 10.6, 210, 44, 45),
        ("Software Engineering", 2600, 9.8, 330, 52, 49),
    ]
    df = pd.DataFrame(rows, columns=["job_family", "headcount", "vol_attrition_pct", "hires_fy26",
                                     "days_to_fill_fy25", "days_to_fill_fy26"])
    df["exits_fy26"] = (df.headcount * df.vol_attrition_pct / 100).round().astype(int)
    df["net_change_fy26"] = df.hires_fy26 - df.exits_fy26
    return df[["job_family", "headcount", "hires_fy26", "exits_fy26", "net_change_fy26",
               "days_to_fill_fy25", "days_to_fill_fy26"]]


def internal_fill_by_fy() -> pd.DataFrame:
    """Firm level, internal. Share of open roles filled by internal candidates, by fiscal year (%)."""
    return pd.DataFrame({"fiscal_year": ["FY22", "FY23", "FY24", "FY25", "FY26"],
                         "internal_fill_pct": [22, 23, 25, 24, 29]})


QUARTERS = [f"Q{q} FY{y}" for y in (24, 25, 26) for q in (1, 2, 3, 4)]


def attrition_quarterly() -> pd.DataFrame:
    """Job-family level, internal. Annualized voluntary attrition by fiscal quarter, Q1 FY24-Q4 FY26 (%).
    The four FY26 quarters average to the FY26 rates in attrition_by_job_family. Pay and scheduling reset for
    Pharmacy Technicians took effect in Q3 FY25."""
    paths = {
        "Pharmacy Technician": [33.6, 34.1, 33.2, 34.4, 33.9, 34.2, 32.8, 31.0, 29.8, 28.0, 26.6, 25.2],
        "Distribution Center Associate": [24.8, 25.3, 24.1, 25.0, 24.6, 23.9, 24.4, 24.8, 24.5, 23.8, 24.3, 23.8],
        "Customer Care": [20.2, 19.6, 19.9, 19.1, 19.4, 18.8, 19.3, 18.9, 19.2, 18.7, 19.1, 18.6],
        "Specialty Nursing": [15.6, 15.1, 15.3, 14.8, 15.0, 14.6, 14.9, 14.4, 14.5, 14.1, 14.3, 13.9],
        "Software Engineering": [12.4, 12.0, 11.7, 11.6, 11.2, 11.0, 10.6, 10.4, 10.1, 9.8, 9.9, 9.4],
        "Finance": [8.1, 7.9, 8.0, 7.8, 7.7, 7.9, 7.6, 7.5, 7.5, 7.3, 7.5, 7.3],
    }
    rows = [(q, fam, v) for fam, vals in paths.items() for q, v in zip(QUARTERS, vals)]
    return pd.DataFrame(rows, columns=["quarter", "job_family", "attrition_pct"])


def data_ai_index() -> pd.DataFrame:
    """Sector vs firm. External Data & AI job postings (healthcare) vs internal Data & AI headcount, indexed 2021 = 100."""
    years = np.arange(2021, 2027)
    postings = [100, 131, 118, 142, 171, 196]
    internal = [100, 104, 109, 113, 118, 122]
    return pd.DataFrame({"year": years, "external_postings_idx": postings, "internal_headcount_idx": internal})


def pharmacist_time_mix() -> pd.DataFrame:
    """Individual -> role level. Share of a retail pharmacist's hours by activity, FY22-FY26 (%), from work sampling."""
    clinical = [12, 15, 21, 27, 31]
    dispensing = [58, 55, 49, 44, 41]
    inventory = [14, 14, 13, 12, 11]
    return pd.DataFrame({"fiscal_year": ["FY22", "FY23", "FY24", "FY25", "FY26"], "clinical_pct": clinical,
                         "dispensing_pct": dispensing, "inventory_pct": inventory,
                         "admin_pct": [100 - c - d - i for c, d, i in zip(clinical, dispensing, inventory)]})


def workforce_reductions() -> pd.DataFrame:
    """Sector level, external. Announced workforce reductions by healthcare sub-sector and quarter (roles affected)."""
    rng = np.random.default_rng(47)
    quarters = [f"{y} Q{q}" for y in range(2020, 2027) for q in (1, 2, 3, 4)][:26]
    spec = {"Pharma manufacturers": (0.25, 900, 0.62, 2600), "Medical devices": (0.35, 700, 0.35, 800),
            "Hospitals & health systems": (0.4, 500, 0.4, 700), "Payers": (0.3, 600, 0.3, 650),
            "Retail pharmacy": (0.3, 800, 0.35, 1100), "Distributors": (0.15, 400, 0.15, 400)}
    rows = []
    for sector, (p_early, s_early, p_late, s_late) in spec.items():
        for i, q in enumerate(quarters):
            late = q >= "2023"
            if rng.random() < (p_late if late else p_early):
                roles = int(rng.gamma(2.0, (s_late if late else s_early) / 2))
                rows.append((sector, q, max(roles, 50) // 10 * 10))
    return pd.DataFrame(rows, columns=["sub_sector", "quarter", "roles_affected"])


def regretted_attrition_bu() -> pd.DataFrame:
    """Business-unit level, internal. Regretted (high-performer) attrition by fiscal quarter, Q1 FY25-Q4 FY26 (%)."""
    paths = {"Corporate": [5.8, 5.6, 5.9, 5.5, 5.7, 5.4, 5.6, 5.3], "Medical-Surgical": [6.4, 6.6, 6.2, 6.5, 6.3, 6.1, 6.4, 6.2],
             "Oncology & Multispecialty": [6.0, 6.6, 7.4, 8.1, 8.9, 9.6, 10.4, 11.2], "RxTS": [5.1, 5.3, 5.0, 5.2, 4.9, 5.1, 4.8, 4.9],
             "Technology": [7.9, 7.6, 7.4, 7.1, 6.9, 6.8, 6.6, 6.4], "U.S. Pharmaceutical": [6.8, 6.9, 6.6, 6.7, 6.5, 6.6, 6.4, 6.5]}
    rows = [(bu, q, v) for bu, vals in paths.items() for q, v in zip(QUARTERS[4:], vals)]
    return pd.DataFrame(rows, columns=["business_unit", "quarter", "regretted_attrition_pct"])


STATE_POP_M = {  # approximate resident population (millions); used only to make synthetic counts scale with size
    "AL": 5.1, "AK": 0.7, "AZ": 7.4, "AR": 3.1, "CA": 39.0, "CO": 5.9, "CT": 3.6, "DE": 1.0, "DC": 0.7, "FL": 22.6,
    "GA": 11.0, "HI": 1.4, "ID": 2.0, "IL": 12.5, "IN": 6.9, "IA": 3.2, "KS": 2.9, "KY": 4.5, "LA": 4.6, "ME": 1.4,
    "MD": 6.2, "MA": 7.0, "MI": 10.0, "MN": 5.7, "MS": 2.9, "MO": 6.2, "MT": 1.1, "NE": 2.0, "NV": 3.2, "NH": 1.4,
    "NJ": 9.3, "NM": 2.1, "NY": 19.6, "NC": 10.8, "ND": 0.8, "OH": 11.8, "OK": 4.0, "OR": 4.2, "PA": 13.0, "RI": 1.1,
    "SC": 5.4, "SD": 0.9, "TN": 7.1, "TX": 30.5, "UT": 3.4, "VT": 0.6, "VA": 8.7, "WA": 7.8, "WV": 1.8, "WI": 5.9,
    "WY": 0.6}


def talent_market_by_state() -> pd.DataFrame:
    """Sector level, external. Pharmacy technician labor market by state: open postings (a count), postings per
    qualified candidate in Q2 2024 and Q2 2026 (a rate), and our technician pay vs. the local market median (%)."""
    rng = np.random.default_rng(26)
    states = sorted(STATE_POP_M)
    r26 = pd.Series(rng.normal(1.05, 0.15, len(states)).clip(0.6, 1.45).round(2), index=states)
    r26.update(pd.Series({"TX": 1.92, "AZ": 1.84, "NV": 1.76, "FL": 1.71, "CO": 1.58, "UT": 1.52}))
    r24 = (r26 * rng.uniform(0.82, 0.97, len(states))).round(2)
    r24.update(pd.Series({"TX": 1.74, "AZ": 1.55, "NV": 1.47, "FL": 1.44, "CO": 1.31, "UT": 1.36}))
    pay = pd.Series(rng.normal(0.8, 2.4, len(states)).clip(-5.5, 5.5).round(1) + 0.0, index=states)  # no "-0.0"
    pay.update(pd.Series({"TX": -7.4, "AZ": -6.6, "FL": -6.2, "NV": -4.8, "CO": -3.1, "MA": 6.4, "WA": 6.1}))
    pop = pd.Series(STATE_POP_M)[states]
    postings = (pop * 46 * r26 * rng.uniform(0.85, 1.15, len(states))).round(-1).astype(int)
    return pd.DataFrame({"state": states, "population_m": pop.values, "open_postings_q2_2026": postings.values,
                         "postings_per_candidate_q2_2024": r24.values, "postings_per_candidate_q2_2026": r26.values,
                         "tech_pay_vs_market_pct": pay.values})


def dc_network() -> pd.DataFrame:
    """Site level, internal. Distribution center associates by site and vacancy rate (open reqs / budgeted), Mar 2026.
    Associates sum to the 11,800 DC Associate headcount; one satellite site has fewer than 10 associates."""
    rows = [("Memphis", "TN", 1680, 13.8), ("Dallas", "TX", 1450, 14.6), ("Columbus", "OH", 1310, 7.2),
            ("Atlanta", "GA", 1180, 8.4), ("Phoenix", "AZ", 980, 12.9), ("Sacramento", "CA", 890, 6.9),
            ("Harrisburg", "PA", 860, 5.8), ("Chicago", "IL", 820, 7.7), ("Kansas City", "MO", 640, 6.1),
            ("Orlando", "FL", 610, 10.4), ("Denver", "CO", 560, 9.6), ("Seattle", "WA", 430, 6.3),
            ("Albany", "NY", 383, 5.1), ("Boise (satellite)", "ID", 7, 0.0)]
    df = pd.DataFrame(rows, columns=["site", "state", "associates", "vacancy_pct"])
    assert df.associates.sum() == 11800
    return df


def remote_care_agents() -> pd.DataFrame:
    """Team level, internal. Remote and hybrid Customer Care agents by home state, aggregated (Mar 2026).
    Hub states host the three contact centers."""
    rng = np.random.default_rng(31)
    hubs = {"TX": 290, "OH": 250, "GA": 210}
    rows = []
    for st, pop in STATE_POP_M.items():
        if st in hubs:
            rows.append((st, hubs[st], True))
        else:
            rows.append((st, int(round(pop * 4.4 * rng.uniform(0.55, 1.45))), False))
    return pd.DataFrame(rows, columns=["state", "agents", "hub_state"]).sort_values("state", kind="stable")


def succession_coverage_bu() -> pd.DataFrame:
    """Business-unit level, internal SWP. Critical roles and those with at least one ready-now successor, Mar 2025
    and Mar 2026 (talent review). Enterprise target: 75% coverage by FY27."""
    rows = [("Corporate", 70, 38, 49), ("Medical-Surgical", 62, 30, 40), ("Oncology & Multispecialty", 48, 19, 21),
            ("RxTS", 40, 24, 31), ("Technology", 85, 36, 50), ("U.S. Pharmaceutical", 105, 50, 63)]
    df = pd.DataFrame(rows, columns=["business_unit", "critical_roles", "ready_now_mar25", "ready_now_mar26"])
    df["target_pct"] = 75
    return df


def skills_profile_completion() -> pd.DataFrame:
    """Function level, internal. Employees with a verified skills profile in the skills inventory, Mar 2025 and
    Mar 2026. Employees = full- and part-time workers in workforce_mix. Target: 80% by FY27."""
    mix = workforce_mix().set_index("function")
    rates = {"Distribution": (0.50, 0.61), "Pharmacy Ops": (0.57, 0.66), "Technology": (0.81, 0.88),
             "Customer Care": (0.60, 0.71), "Corporate": (0.70, 0.79)}
    rows = []
    for fn, (r25, r26) in rates.items():
        emp = int(round(mix.workers[fn] * (mix.employee_ft_pct[fn] + mix.employee_pt_pct[fn]) / 100))
        rows.append((fn, emp, int(round(emp * r25)), int(round(emp * r26)), 80))
    return pd.DataFrame(rows, columns=["function", "employees", "profiles_mar25", "profiles_mar26", "target_pct"])
def dc_vacancy_overtime() -> pd.DataFrame:
    """Site level, internal. U.S. distribution centers, monthly Jan 2025-Dec 2026: vacancy rate (% of budgeted roles
    open at month end) and paid overtime (hours per worked FTE per week). Same values as docs/cookbook/dual-axis.md."""
    months = pd.date_range("2025-01-01", "2026-12-01", freq="MS").strftime("%b %Y")
    vacancy = [7.2, 7.5, 7.9, 8.4, 9.1, 9.8, 10.6, 11.4, 12.1, 12.6, 12.3, 11.8,
               11.0, 10.2, 9.5, 8.9, 8.4, 8.1, 7.9, 7.7, 7.6, 7.4, 7.3, 7.2]
    overtime = [3.9, 4.0, 4.3, 4.6, 5.0, 5.5, 5.9, 6.3, 6.6, 6.8, 6.7, 6.4,
                6.0, 5.6, 5.2, 4.9, 4.7, 4.5, 4.4, 4.3, 4.3, 4.2, 4.1, 4.1]
    return pd.DataFrame({"month": months, "vacancy_pct": vacancy, "overtime_hrs_per_fte_wk": overtime})


def reskilling_pipeline() -> pd.DataFrame:
    """Program level, internal. Data & AI reskilling academy, FY25-FY26 cohorts: flows between stages (people).
    transfer: progressed / dropped / not_placed. Same values as docs/cookbook/sankey.md; every flow is n >= 10."""
    rows = [("Nominated", "Enrolled", 1010, "progressed"), ("Nominated", "Declined", 190, "dropped"),
            ("Enrolled", "Completed", 840, "progressed"), ("Enrolled", "Withdrew", 170, "dropped"),
            ("Completed", "Redeployed to data role", 410, "progressed"),
            ("Completed", "Returned to prior role", 350, "not_placed"), ("Completed", "Left McKesson", 80, "not_placed")]
    return pd.DataFrame(rows, columns=["from_stage", "to_stage", "people", "transfer"])
def internal_fill_by_bu() -> pd.DataFrame:
    """Business-unit level, internal. Share of open roles filled by internal candidates, by fiscal year (%).
    Ranks match the bump chart in docs/cookbook/slope-bump.md; the yearly averages track internal_fill_by_fy."""
    paths = {"Technology": [14, 19, 27, 29, 41], "U.S. Pharmaceutical": [28, 29, 29, 30, 32],
             "Medical-Surgical": [26, 25, 30, 26, 30], "RxTS": [21, 26, 25, 24, 27],
             "Corporate": [19, 17, 18, 19, 25], "Oncology & Multispecialty": [24, 22, 21, 18, 21]}
    rows = [(bu, fy, v) for bu, vals in paths.items() for fy, v in zip(["FY22", "FY23", "FY24", "FY25", "FY26"], vals)]
    return pd.DataFrame(rows, columns=["business_unit", "fiscal_year", "internal_fill_pct"])


def span_of_control() -> pd.DataFrame:
    """Manager level, internal. Direct reports per U.S. people manager, Mar 2026 (one row per manager, no IDs).
    Same generator as the histogram snippet in docs/cookbook/distribution.md."""
    rng = np.random.default_rng(11)
    span = np.r_[rng.poisson(7, 900), rng.poisson(13, 380), rng.poisson(24, 100)].clip(1, 40)
    return pd.DataFrame({"direct_reports": span.astype(int)})


def data_ai_talent_by_country() -> pd.DataFrame:
    """Country level, external and internal. Data & AI talent in the countries assessed for a global capability
    center, Q2 2026: qualified candidates per open Data & AI role (a rate, from external postings and profiles) and
    our Data & AI people by work country (a count; the U.S. figure is the Data & Analytics headcount, 850).
    iso_n3 is the ISO 3166 numeric code (the id in world-atlas)."""
    rows = [("United States", "840", 2.1, 850),
            ("Canada", "124", 3.4, 140),
            ("Mexico", "484", 4.6, 6),
            ("Brazil", "076", 5.2, 0),
            ("Argentina", "032", 4.1, 0),
            ("Colombia", "170", 4.8, 0),
            ("Chile", "152", 3.2, 0),
            ("United Kingdom", "826", 2.6, 0),
            ("Ireland", "372", 1.8, 60),
            ("Germany", "276", 1.6, 0),
            ("France", "250", 2.4, 0),
            ("Netherlands", "528", 1.7, 0),
            ("Spain", "724", 3.6, 0),
            ("Portugal", "620", 4.4, 0),
            ("Poland", "616", 5.6, 8),
            ("Romania", "642", 6.3, 0),
            ("Czechia", "203", 3.8, 0),
            ("Israel", "376", 1.5, 24),
            ("Egypt", "818", 7.1, 0),
            ("South Africa", "710", 4.9, 0),
            ("India", "356", 9.4, 380),
            ("Philippines", "608", 8.3, 0),
            ("Vietnam", "704", 7.4, 0),
            ("Malaysia", "458", 5.1, 0),
            ("Japan", "392", 1.4, 0),
            ("South Korea", "410", 2.2, 0),
            ("Australia", "036", 2.0, 0)]
    return pd.DataFrame(rows, columns=["country", "iso_n3", "candidates_per_role_2026", "our_data_ai_people"])


def pharm_tech_north_texas() -> pd.DataFrame:
    """County level, external. Pharmacy technician labor market in the 19 counties whose centre is within 70 miles
    of our Irving campus, Q2 2026: qualified candidates, open postings and postings per candidate (the same rate as
    talent_market_by_state, where Texas is 1.92). Two rural counties have fewer than 10 candidates: never show them.
    fips matches the us-atlas county ids; population is the 2020 census in thousands, rounded."""
    rng = np.random.default_rng(48)
    counties = [("48113", "Dallas", 2614, 2.14), ("48439", "Tarrant", 2111, 1.78), ("48121", "Denton", 906, 1.83),
                ("48085", "Collin", 1064, 1.96), ("48397", "Rockwall", 108, 1.52), ("48139", "Ellis", 192, 1.44),
                ("48251", "Johnson", 180, 1.38), ("48257", "Kaufman", 145, 1.31), ("48497", "Wise", 69, 1.12),
                ("48367", "Parker", 148, 1.47), ("48231", "Hunt", 100, 1.06), ("48217", "Hill", 36, 0.74),
                ("48221", "Hood", 62, 1.16), ("48181", "Grayson", 136, 1.21), ("48097", "Cooke", 42, 0.93),
                ("48349", "Navarro", 53, 0.88), ("48425", "Somervell", 9, None), ("48467", "Van Zandt", 60, 0.79),
                ("48379", "Rains", 12, None)]
    rows = []
    for fips, name, pop, ratio in counties:
        cand = int(round(pop * 0.6 * rng.uniform(0.85, 1.15)))
        ratio = ratio if ratio is not None else round(rng.uniform(0.5, 2.5), 2)    # noisy where n is tiny
        post = int(round(cand * ratio))
        rows.append((fips, name, pop, cand, post, round(post / cand, 2)))
    return pd.DataFrame(rows, columns=["fips", "county", "population_k", "qualified_candidates", "open_postings",
                                       "postings_per_candidate"])


def initiative_plan() -> pd.DataFrame:
    """Program level, internal. The Workforce Innovation FY26-FY27 roadmap as reported at the March 2026 steering
    committee (as of 31 Mar 2026; McKesson's fiscal year starts in April). One row per workstream; owners are roles.
    start / end are months (YYYY-MM, inclusive). status is a color.status key: off_track = a milestone missed with
    no recovery date, at_risk = a milestone moved with a recovery date set. depends_on names the workstream it waits
    for. what_changed = since the February report. Milestones are in initiative_milestones."""
    rows = [
        ("Workforce data platform", "HR data platform lead", "2025-04", "2026-09", "on_track", "",
         "Learning data now loads daily", 64),
        ("Skills inventory rollout", "Talent systems director", "2025-04", "2027-03", "at_risk", "",
         "Workday integration moved from Mar to Jun after failed testing", 71),
        ("SWP model refresh", "SWP lead", "2025-10", "2026-09", "off_track", "Skills inventory rollout",
         "Model build paused until skills data reaches Workday", 38),
        ("Gen AI reskilling", "Learning director", "2026-01", "2027-03", "off_track", "Skills inventory rollout",
         "Cohort 1 can't be picked without skills data", 12),
        ("Pharmacy technician career path", "Pharmacy Ops talent lead", "2025-07", "2026-12", "on_track", "",
         "Curriculum approved by pharmacy leaders", 45),
        ("DC scheduling pilot", "DC operations director", "2025-07", "2026-03", "done", "",
         "Pilot closed on plan; scale-up decision in April", 96),
        ("Succession refresh", "Talent management director", "2026-07", "2027-03", "not_started", "",
         "No change; starts with the FY27 talent review", 0),
    ]
    return pd.DataFrame(rows, columns=["workstream", "owner", "start", "end", "status", "depends_on", "what_changed",
                                       "budget_used_pct"])


def initiative_milestones() -> pd.DataFrame:
    """Milestones for initiative_plan (as of 31 Mar 2026). due = baseline month; forecast = current expected month
    (blank when missed with no recovery date). state: met, moved (forecast later than due), missed, upcoming."""
    rows = [
        ("Workforce data platform", "Architecture signed off", "2025-06", "2025-06", "met"),
        ("Workforce data platform", "Workday data live", "2025-10", "2025-10", "met"),
        ("Workforce data platform", "Learning data live", "2026-02", "2026-02", "met"),
        ("Workforce data platform", "Self-serve dashboards live", "2026-06", "2026-06", "upcoming"),
        ("Skills inventory rollout", "Skills taxonomy approved", "2025-06", "2025-06", "met"),
        ("Skills inventory rollout", "Profiles open to all employees", "2025-09", "2025-09", "met"),
        ("Skills inventory rollout", "Workday integration live", "2026-03", "2026-06", "moved"),
        ("Skills inventory rollout", "80% of profiles verified", "2027-03", "2027-03", "upcoming"),
        ("SWP model refresh", "Demand drivers updated", "2025-12", "2025-12", "met"),
        ("SWP model refresh", "Skills supply feed", "2026-02", "", "missed"),
        ("SWP model refresh", "FY28 plan scenarios", "2026-08", "2026-08", "upcoming"),
        ("Gen AI reskilling", "Curriculum designed", "2026-02", "2026-02", "met"),
        ("Gen AI reskilling", "Cohort 1 selected", "2026-03", "", "missed"),
        ("Gen AI reskilling", "Cohort 1 complete", "2026-10", "2026-10", "upcoming"),
        ("Gen AI reskilling", "Cohort 2 complete", "2027-03", "2027-03", "upcoming"),
        ("Pharmacy technician career path", "Career levels defined", "2025-09", "2025-09", "met"),
        ("Pharmacy technician career path", "Curriculum approved", "2026-02", "2026-02", "met"),
        ("Pharmacy technician career path", "Level II pilot starts", "2026-05", "2026-05", "upcoming"),
        ("Pharmacy technician career path", "Enterprise rollout", "2026-11", "2026-11", "upcoming"),
        ("DC scheduling pilot", "Pilot sites live", "2025-10", "2025-10", "met"),
        ("DC scheduling pilot", "Results to steering committee", "2026-03", "2026-03", "met"),
        ("Succession refresh", "Talent review kickoff", "2026-07", "2026-07", "upcoming"),
        ("Succession refresh", "Successor slates approved", "2027-01", "2027-01", "upcoming"),
    ]
    return pd.DataFrame(rows, columns=["workstream", "milestone", "due", "forecast", "state"])


def initiative_status_history() -> pd.DataFrame:
    """Monthly reported status per workstream in initiative_plan, Oct 2025-Mar 2026 (color.status keys)."""
    months = ["2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03"]
    on, risk, off, ns, done = "on_track", "at_risk", "off_track", "not_started", "done"
    hist = {"Workforce data platform": [on, on, on, on, on, on],
            "Skills inventory rollout": [on, on, on, risk, risk, risk],
            "SWP model refresh": [on, on, on, risk, off, off],
            "Gen AI reskilling": [ns, ns, ns, on, risk, off],
            "Pharmacy technician career path": [on, risk, risk, on, on, on],
            "DC scheduling pilot": [on, on, on, on, on, done],
            "Succession refresh": [ns, ns, ns, ns, ns, ns]}
    return pd.DataFrame([(w, m, s) for w, ss in hist.items() for m, s in zip(months, ss)],
                        columns=["workstream", "month", "status"])


def main() -> None:
    sets = {
        "attrition_quarterly": attrition_quarterly(),
        "data_ai_index": data_ai_index(),
        "pharmacist_time_mix": pharmacist_time_mix(),
        "workforce_reductions": workforce_reductions(),
        "regretted_attrition_bu": regretted_attrition_bu(),
        "hiring_flow_by_family": hiring_flow_by_family(),
        "tech_mix_by_fy": tech_mix_by_fy(),
        "data_ai_gap_plan": data_ai_gap_plan(),
        "engagement_items": engagement_items(),
        "headcount_bridge": headcount_bridge(),
        "internal_fill_by_fy": internal_fill_by_fy(),
        "attrition_by_job_family": attrition_by_job_family(),
        "data_ai_supply_demand": data_ai_supply_demand(),
        "automation_exposure": automation_exposure(),
        "labor_cost_bridge": labor_cost_bridge(),
        "mobility_flows": mobility_flows(),
        "engagement_vs_benchmark": engagement_vs_benchmark(),
        "pay_vs_market": pay_vs_market(),
        "skills_demand_rank": skills_demand_rank(),
        "workforce_mix": workforce_mix(),
        "compa_ratio_individuals": compa_ratio_individuals(),
        "job_family_scorecard": job_family_scorecard(),
        "skills_overlap": skills_overlap(),
        "talent_market_by_state": talent_market_by_state(),
        "dc_network": dc_network(),
        "remote_care_agents": remote_care_agents(),
        "succession_coverage_bu": succession_coverage_bu(),
        "skills_profile_completion": skills_profile_completion(),
        "dc_vacancy_overtime": dc_vacancy_overtime(),
        "reskilling_pipeline": reskilling_pipeline(),
        "internal_fill_by_bu": internal_fill_by_bu(),
        "span_of_control": span_of_control(),
        "data_ai_talent_by_country": data_ai_talent_by_country(),
        "pharm_tech_north_texas": pharm_tech_north_texas(),
        "initiative_plan": initiative_plan(),
        "initiative_milestones": initiative_milestones(),
        "initiative_status_history": initiative_status_history(),
    }
    for name, df in sets.items():
        df.to_csv(OUT / f"{name}.csv", index=False)
        print(f"wrote {name}.csv ({len(df)} rows)")


if __name__ == "__main__":
    main()
