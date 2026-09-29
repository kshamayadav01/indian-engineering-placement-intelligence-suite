import os
import re
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DB_PATH = "campus_placement.db"
CSV_PATH = "indian_engineering_placement_2026.csv"

st.set_page_config(
    page_title="placement intelligent & analytics suite",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------
# Database setup
# --------------------------------------------------------------------

def init_db():
    if not os.path.exists(CSV_PATH):
        st.error(f"Source file '{CSV_PATH}' not found in the current directory.")
        st.stop()

    df = pd.read_csv(CSV_PATH)

    # Normalize column names to lowercase snake_case
    df.columns = [
        re.sub(r"[^a-zA-Z0-9]+", "_", str(col)).strip("_").lower()
        for col in df.columns
    ]

    # Fill missing values for important columns
    if "open_source_contributions" in df.columns:
        df["open_source_contributions"] = df["open_source_contributions"].fillna(
            df["open_source_contributions"].median()
        )

    if "linkedin_activity_score" in df.columns:
        df["linkedin_activity_score"] = df["linkedin_activity_score"].fillna(
            df["linkedin_activity_score"].median()
        )

    # Normalize string fields to consistent lowercase values
    for col in ["college_tier", "branch", "placement_status", "gender"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.lower()

    conn = sqlite3.connect(DB_PATH)
    df.to_sql("students", con=conn, if_exists="replace", index=False)

    cursor = conn.cursor()
    cursor.executescript("""
        CREATE INDEX IF NOT EXISTS idx_tier ON students(college_tier);
        CREATE INDEX IF NOT EXISTS idx_branch ON students(branch);
        CREATE INDEX IF NOT EXISTS idx_placement ON students(placement_status);
        CREATE INDEX IF NOT EXISTS idx_cgpa ON students(cgpa);
        CREATE INDEX IF NOT EXISTS idx_dsa ON students(dsa_problems_solved);
    """)

    conn.commit()
    conn.close()


def ensure_db_ready():
    required_columns = {
        "student_id",
        "age",
        "gender",
        "state",
        "branch",
        "college_tier",
        "cgpa",
        "attendance_percentage",
        "dsa_problems_solved",
        "aptitude_score",
        "communication_score",
        "projects_count",
        "internships_count",
        "certifications_count",
        "open_source_contributions",
        "github_contributions",
        "linkedin_activity_score",
        "hackathons_participated",
        "competitive_programming_rating",
        "study_hours_per_week",
        "soft_skills_score",
        "leadership_experience",
        "extracurricular_activities",
        "placement_status",
        "package_lpa",
    }

    if not os.path.exists(DB_PATH):
        with st.spinner("Initializing SQLite database..."):
            init_db()
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='students'"
    )
    table_exists = cursor.fetchone()

    if not table_exists:
        conn.close()
        with st.spinner("Creating students table..."):
            init_db()
        return

    existing_columns = {
        row[1]
        for row in cursor.execute("PRAGMA table_info(students)").fetchall()
    }
    conn.close()

    missing_columns = sorted(required_columns - existing_columns)
    if missing_columns:
        os.remove(DB_PATH)
        with st.spinner("Refreshing SQLite schema from the source CSV..."):
            init_db()


ensure_db_ready()


def run_query(query: str, params: tuple = ()) -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn, params=params)


# --------------------------------------------------------------------
# Sidebar filters
# --------------------------------------------------------------------

st.sidebar.title("☺️ Cohort Filters")

tier_opts = [
    r[0] for r in run_query(
        "SELECT DISTINCT college_tier FROM students ORDER BY college_tier"
    ).values
]
branch_opts = [
    r[0] for r in run_query(
        "SELECT DISTINCT branch FROM students ORDER BY branch"
    ).values
]

selected_tiers = st.sidebar.multiselect(
    "Institutional Tier", tier_opts, default=tier_opts
)
selected_branches = st.sidebar.multiselect(
    "Branch", branch_opts, default=branch_opts
)

cgpa_range = st.sidebar.slider(
    "CGPA Range", 5.0, 10.0, (5.0, 10.0), 0.1
)
min_dsa = st.sidebar.slider(
    "Minimum DSA Problems Solved", 0, 1200, 0, 50
)

if not selected_tiers or not selected_branches:
    st.warning("Please select at least one tier and one branch from the sidebar.")
    st.stop()

# Build SQL parameterized filter
tier_placeholders = ",".join("?" for _ in selected_tiers)
branch_placeholders = ",".join("?" for _ in selected_branches)

where_clause = f"""
    WHERE college_tier IN ({tier_placeholders})
    AND branch IN ({branch_placeholders})
    AND cgpa BETWEEN ? AND ?
    AND dsa_problems_solved >= ?
"""

filter_params = tuple(
    selected_tiers + selected_branches + [cgpa_range[0], cgpa_range[1], min_dsa]
)

cohort_data = run_query(f"SELECT * FROM students {where_clause};", filter_params)

if cohort_data.empty:
    st.warning("No students match the selected filters.")
    st.stop()

placed_cohort = cohort_data[cohort_data["placement_status"] == "placed"]

# KPI calculations
total_count = len(cohort_data)
placed_count = len(placed_cohort)
rate = (placed_count / total_count * 100) if total_count else 0.0
avg_lpa = placed_cohort["package_lpa"].mean() if not placed_cohort.empty else 0
peak_lpa = placed_cohort["package_lpa"].max() if not placed_cohort.empty else 0

# --------------------------------------------------------------------
# Executive KPI metrics
# --------------------------------------------------------------------

st.title("Indian Engineering Placement Intelligence Suite")
st.caption("10 high-dimensional visualizations | dynamic SQL queries | future trends")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Active cohort size", f"{total_count:,}")
k2.metric("Placement rate", f"{rate:.1f}%")
k3.metric("Avg package (placed)", f"₹{avg_lpa:.2f} LPA")
k4.metric("Highest package", f"₹{peak_lpa:.2f} LPA")

st.divider()

# --------------------------------------------------------------------
# Tabs
# --------------------------------------------------------------------

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Core drivers",
        "Institutional & branches",
        "Skill benchmarks",
        "Future projection",
        "SQL sandbox",
    ]
)

# --------------------------------------------------------------------
# TAB 1: Core drivers
# --------------------------------------------------------------------

with tab1:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("1. Package (LPA) vs DSA problems solved")
        if not placed_cohort.empty:
            scatter_df = placed_cohort.sample(
                min(1500, len(placed_cohort)), random_state=42
            )

            fig1 = px.scatter(
                scatter_df,
                x="dsa_problems_solved",
                y="package_lpa",
                color="college_tier",
                size="github_contributions",
                size_max=16,
                opacity=0.75,
                color_discrete_map={
                    "tier-1": "#1f77b4",
                    "tier-2": "#ff7f0e",
                    "tier-3": "#2ca02c",
                },
                labels={
                    "dsa_problems_solved": "DSA problems",
                    "package_lpa": "Package (LPA)",
                },
                title="<b>Problem solving vs compensation (sized by GitHub contributions)</b>",
            )

            fig1.update_traces(
                customdata=scatter_df[["student_id", "branch", "cgpa", "internships_count"]].values,
                hovertemplate=(
                    "<b>ID:</b> %{customdata[0]}<br>"
                    "<b>Branch:</b> %{customdata[1]}<br>"
                    "<b>CGPA:</b> %{customdata[2]:.2f}<br>"
                    "<b>DSA solved:</b> %{x}<br>"
                    "<b>Internships:</b> %{customdata[3]}<br>"
                    "<b>Package:</b> ₹%{y:.2f} LPA<extra></extra>"
                ),
            )
            fig1.update_layout(template="plotly_white")
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No placed records for scatter plot.")

    with c2:
        st.subheader("2. Placement probability matrix (internships vs projects)")
        pivot = cohort_data.pivot_table(
            index="projects_count",
            columns="internships_count",
            values="placement_status",
            aggfunc=lambda s: (s == "placed").mean() * 100,
        ).fillna(0)

        fig2 = px.imshow(
            pivot,
            text_auto=".1f",
            color_continuous_scale="blues",
            labels={
                "x": "Internships completed",
                "y": "Projects count",
                "color": "Placement rate (%)",
            },
            title="<b>Placement rate matrix (%): projects vs internships</b>",
        )
        fig2.update_layout(template="plotly_white")
        st.plotly_chart(fig2, use_container_width=True)

# --------------------------------------------------------------------
# TAB 2: Institutional & branch comparison
# --------------------------------------------------------------------

with tab2:
    c3, c4 = st.columns(2)

    with c3:
        st.subheader("3. Placement conversion & package by branch")
        branch_summary = (
            cohort_data.groupby("branch", observed=False)
            .agg(
                placement_rate=("placement_status", lambda x: (x == "placed").mean() * 100),
                avg_package=("package_lpa", lambda x: x[x > 0].mean() if len(x[x > 0]) > 0 else 0),
            )
            .reset_index()
            .sort_values(by="placement_rate", ascending=False)
        )

        fig3 = px.bar(
            branch_summary,
            x="branch",
            y="placement_rate",
            color="avg_package",
            color_continuous_scale="Viridis",
            text="placement_rate",
            labels={
                "placement_rate": "Placement rate (%)",
                "avg_package": "Avg package (LPA)",
            },
            title="<b>Branch success rate & starting CTC</b>",
        )
        fig3.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig3.update_layout(yaxis=dict(range=[0, 110]), template="plotly_white")
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        st.subheader("4. Package spread by college tier")
        if not placed_cohort.empty:
            fig4 = px.box(
                placed_cohort,
                x="college_tier",
                y="package_lpa",
                color="college_tier",
                category_orders={"college_tier": ["tier-1", "tier-2", "tier-3"]},
                labels={"package_lpa": "Package (LPA)"},
                title="<b>Institutional tier salary distributions & outliers</b>",
            )
            fig4.update_layout(showlegend=False, template="plotly_white")
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("No records available.")

    st.subheader("5. Student flow hierarchy: tier + branch + status")
    sample_hierarchy = cohort_data.sample(min(4000, len(cohort_data)), random_state=42)

    fig5 = px.sunburst(
        sample_hierarchy,
        path=["college_tier", "branch", "placement_status"],
        values="cgpa",
        color="package_lpa",
        color_continuous_scale="RdBu_r",
        title="<b>Multi-level sunburst of academic hierarchy & salary concentration</b>",
    )

    fig5.update_layout(template="plotly_white")
    st.plotly_chart(fig5, use_container_width=True)

# --------------------------------------------------------------------
# TAB 3: Skill benchmarks & density
# --------------------------------------------------------------------

with tab3:
    c5, c6 = st.columns(2)

    with c5:
        st.subheader("6. Competency radar: elite (≥ 20 LPA) vs baseline")
        radar_metrics = [
            "cgpa",
            "dsa_problems_solved",
            "aptitude_score",
            "communication_score",
            "soft_skills_score",
        ]

        scaled_df = cohort_data.copy()
        scaled_df["cgpa"] = (scaled_df["cgpa"] / 10.0) * 100
        scaled_df["dsa_problems_solved"] = (
            (scaled_df["dsa_problems_solved"] / 500.0).clip(upper=1.0) * 100
        )

        elite_means = (
            scaled_df[scaled_df["package_lpa"] >= 20.0][radar_metrics].mean().tolist()
        )
        base_means = scaled_df[radar_metrics].mean().tolist()

        radar_labels = ["CGPA (scaled)", "DSA (scaled)", "Aptitude", "Communication", "Soft Skills"]
        radar_labels += [radar_labels[0]]
        elite_means += [elite_means[0] if elite_means else 0]
        base_means += [base_means[0] if base_means else 0]

        fig6 = go.Figure()
        fig6.add_trace(
            go.Scatterpolar(
                r=elite_means,
                theta=radar_labels,
                fill="toself",
                name="High package (≥ 20 LPA)",
                line_color="#1f77b4",
            )
        )

        fig6.add_trace(
            go.Scatterpolar(
                r=base_means,
                theta=radar_labels,
                fill="toself",
                name="Cohort average",
                line_color="#636efa",
            )
        )

        fig6.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            title="<b>Holistic skill profile comparison</b>",
            template="plotly_white",
        )

        st.plotly_chart(fig6, use_container_width=True)

    with c6:
        st.subheader("7. Package distribution density by branch & gender")
        if not placed_cohort.empty:
            fig7 = px.violin(
                placed_cohort,
                x="branch",
                y="package_lpa",
                color="gender",
                box=True,
                points=False,
                color_discrete_map={"male": "#3882F6", "female": "#EC4899"},
                title="<b>Compensation density & gender parity</b>",
            )
            fig7.update_layout(template="plotly_white")
            st.plotly_chart(fig7, use_container_width=True)
        else:
            st.info("No data available.")

st.subheader("8. Package frequency & density distribution")

if not placed_cohort.empty:
    fig8 = px.histogram(
        placed_cohort,
        x="package_lpa",
        nbins=40,
        marginal="rug",
        color="college_tier",
        title="<b>Distribution of starting compensation (LPA)</b>",
    )
    fig8.update_layout(template="plotly_white")
    st.plotly_chart(fig8, use_container_width=True)

# --------------------------------------------------------------------
# TAB 4: Future projections & funnel
# --------------------------------------------------------------------

with tab4:
    c7, c8 = st.columns(2)

    with c7:
        st.subheader("9. Future projection: skill-driven marginal returns")

        if not placed_cohort.empty:
            dsa_bins = pd.cut(
                placed_cohort["dsa_problems_solved"],
                bins=range(0, 1200, 100),
            )

            dsa_pkg = (
                placed_cohort.groupby(dsa_bins, observed=False)["package_lpa"]
                .mean()
                .reset_index()
            )
            dsa_pkg["bin_mid"] = [b.mid for b in dsa_pkg["dsa_problems_solved"]]
            dsa_pkg = dsa_pkg.dropna()
            dsa_pkg["future_curve"] = dsa_pkg["package_lpa"] * (
                1 + (dsa_pkg["bin_mid"] / 1000) * 0.35
            )

            fig9 = go.Figure()
            fig9.add_trace(
                go.Scatter(
                    x=dsa_pkg["bin_mid"],
                    y=dsa_pkg["package_lpa"],
                    mode="lines+markers",
                    name="Current cohort baseline",
                    line=dict(color="#2E8B57", width=3),
                )
            )
            fig9.add_trace(
                go.Scatter(
                    x=dsa_pkg["bin_mid"],
                    y=dsa_pkg["future_curve"],
                    mode="lines+markers",
                    name="Projected 2027-2028 premium",
                    line=dict(color="#F4A44D", dash="dash", width=3),
                )
            )

            fig9.update_layout(
                title="<b>Projected CTC growth by DSA milestone solved</b>",
                xaxis_title="DSA problems solved milestone",
                yaxis_title="Package (LPA)",
                template="plotly_white",
            )
            st.plotly_chart(fig9, use_container_width=True)
        else:
            st.info("Insufficient data for future projection.")

    with c8:
        st.subheader("10. Hiring conversion pipeline (funnel)")

        n_total = len(cohort_data)
        n_cgpa = len(cohort_data[cohort_data["cgpa"] >= 7.0])
        n_intern = len(
            cohort_data[
                (cohort_data["cgpa"] >= 7.0)
                & (cohort_data["internships_count"] >= 1)
            ]
        )
        n_dsa = len(
            cohort_data[
                (cohort_data["cgpa"] >= 7.0)
                & (cohort_data["internships_count"] >= 1)
                & (cohort_data["dsa_problems_solved"] >= 150)
            ]
        )
        n_placed = len(
            cohort_data[
                (cohort_data["cgpa"] >= 7.0)
                & (cohort_data["internships_count"] >= 1)
                & (cohort_data["dsa_problems_solved"] >= 150)
                & (cohort_data["placement_status"] == "placed")
            ]
        )

        fig10 = go.Figure(
            go.Funnel(
                y=[
                    "Total candidates",
                    "CGPA ≥ 7.0 (shortlisted)",
                    "Internships ≥ 1",
                    "DSA ≥ 150 (tech rounds)",
                    "Placed candidates",
                ],
                x=[n_total, n_cgpa, n_intern, n_dsa, n_placed],
                textinfo="value+percent initial",
            )
        )

        fig10.update_layout(
            title="<b>Student transition funnel through criteria</b>",
            template="plotly_white",
        )
        st.plotly_chart(fig10, use_container_width=True)

# --------------------------------------------------------------------
# TAB 5: SQL sandbox
# --------------------------------------------------------------------

with tab5:
    st.subheader("11. Ad-hoc SQL execution sandbox")

    st.markdown(
        "Run custom SQL queries against the students table."
    )

    default_sql = """SELECT
    college_tier,
    COUNT(*) AS total_students,
    ROUND(AVG(dsa_problems_solved), 0) AS avg_dsa,
    ROUND(
        100.0 * SUM(
            CASE
                WHEN placement_status = 'placed' THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS placement_rate_pct,
    ROUND(
        AVG(
            CASE
                WHEN placement_status = 'placed'
                THEN package_lpa
                ELSE NULL
            END
        ),
        2
    ) AS avg_placed_package_lpa
    FROM students
    GROUP BY college_tier
    ORDER BY avg_placed_package_lpa DESC;"""

    user_sql = st.text_area("SQL Editor:", value=default_sql, height=140)

    if st.button("Execute Query"):
        try:
            res_df = run_query(user_sql)
            st.dataframe(res_df, use_container_width=True)
            st.success(f"Returned {len(res_df)} rows.")
        except Exception as err:
            st.error(f"SQL Execution Error: {err}")




























