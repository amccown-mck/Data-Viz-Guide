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
    return df.sort_values("vol_attrition_pct", ascending=False)


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
    return df.sort_values("gap_pct")


def skills_demand_rank() -> pd.DataFrame:
    """Sector level, external. Rank of skills in healthcare-distribution job postings, 2023 vs 2026."""
    rows = [("Inventory management", 1, 3), ("Customer service", 2, 5), ("Regulatory compliance", 3, 2),
            ("Data analysis", 4, 1), ("Automation / robotics", 5, 4), ("Clinical documentation", 6, 7),
            ("Sales & negotiation", 7, 8), ("Project management", 8, 9), ("Gen AI / prompt design", 9, 6)]
    return pd.DataFrame(rows, columns=["skill", "rank_2023", "rank_2026"])


def workforce_mix() -> pd.DataFrame:
    """Function level. Share of workforce by employment type (%)."""
    rows = [("Distribution", 71, 22, 7), ("Pharmacy Ops", 83, 12, 5), ("Technology", 58, 12, 30),
            ("Customer Care", 64, 30, 6), ("Corporate", 88, 4, 8)]
    return pd.DataFrame(rows, columns=["function", "employee_ft_pct", "employee_pt_pct", "contingent_pct"])


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
    """Firm level, internal. One row per job family: size, attrition, hiring and engagement (FY26)."""
    rows = [
        ("Pharmacy Technician", 6200, 27.4, 3.1, 52, 31, 68),
        ("Distribution Center Associate", 11800, 24.1, 1.8, 24, 18, 66),
        ("Customer Care", 3100, 18.9, -0.6, 29, 22, 71),
        ("Specialty Nursing", 1400, 14.2, -1.2, 71, 26, 74),
        ("Data & Analytics", 850, 12.9, 0.4, 58, 41, 77),
        ("Supply Chain Planning", 900, 11.8, -0.3, 47, 44, 75),
        ("Sales", 2300, 10.6, -0.9, 45, 35, 76),
        ("Software Engineering", 2600, 9.8, -2.1, 49, 29, 74),
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


def main() -> None:
    sets = {
        "hiring_flow_by_family": hiring_flow_by_family(),
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
    }
    for name, df in sets.items():
        df.to_csv(OUT / f"{name}.csv", index=False)
        print(f"wrote {name}.csv ({len(df)} rows)")


if __name__ == "__main__":
    main()
