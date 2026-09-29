import plotly.express as px
import pandas as pd

def render_placement_scatter(df: pd.DataFrame):
    fig = px.scatter(
        df,
        x="DSA_Problems_Solved",
        y="Package_LPA",
        color="College_Tier",
        size="GitHub_Contributions",
        size_max=18,
        opacity=0.75,
        color_discrete_map={
            "Tier-1": "#1f77b4",
            "Tier-2": "#ff7f0e",
            "Tier-3": "#2ca02c"
        },
        category_orders={"College_Tier": ["Tier-1", "Tier-2", "Tier-3"]},
        title="<b>Package (LPA) vs. DSA Problems Solved</b>",
        labels={
            "DSA_Problems_Solved": "DSA Problems Solved",
            "Package_LPA": "Package (LPA)",
            "College_Tier": "College Tier"
        }
    )

    fig.update_traces(
        hovertemplate=
            "<b>Candidate ID:</b> %{customdata[0]}<br>"
            "<b>Branch:</b> %{customdata[1]}<br>"
            "<b>College Tier:</b> %{customdata[2]}<br>"
            "<b>CGPA:</b> %{customdata[3]:.2f}<br>"
            "<b>DSA Solved:</b> %{x}<br>"
            "<b>GitHub Contributions:</b> %{customdata[4]}<br>"
            "<b>Compensation:</b> %{y:.2f} LPA"
            "<extra></extra>"
        ),

    customdata=df[["Student_ID", "Branch", "College_Tier", "CGPA", "GitHub_Contributions"]].values
    
    fig.update_layout(
        template="plotly_white",
        hoverlabel=dict(bgcolor="white", font_size=12),
        xaxis=dict(title="<b>DSA problems solved</>",gridcolor="#f0f0f0"),
        yaxis=dict(title="<b>package(LPA)</b>",gridcolor="#f0f0f0"),           
        legend=dict(title="Institutional Tier",orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1)    
    )

    return fig


def render_branch_bar(df: pd.DataFrame):
    chart_df = df.copy()

    if chart_df.empty:
        return px.bar(title="<b>Branch-wise Placement Rate</b>")

    chart_df = chart_df.sort_values("Placement_Rate", ascending=False)

    fig = px.bar(
        chart_df,
        x="Branch",
        y="Placement_Rate",
        color="Placement_Rate",
        color_continuous_scale="Viridis",
        text="Placement_Rate",
        title="<b>Branch-wise Placement Rate</b>",
        labels={"Branch": "Branch","Placement_Rate": "Placement Rate (%)","Avg_Package": "Avg Package (LPA)"
        },
        hover_data={"Avg_Package": ":.2f"}
    )

    fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside",
        hovertemplate=(
            "<b>Branch:</b> %{x}<br>"
            "<b>Placement Rate:</b> %{y:.2f}%<br>"
            "<b>Avg Package:</b> %{customdata[0]:.2f} LPA"
            "<extra></extra>"
        ),
        customdata=chart_df[["Avg_Package"]].values
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Branch",
        yaxis_title="Placement Rate (%)",
        showlegend=False,
        height=420
    )

    return fig


def render_correlation_heatmap(df: pd.DataFrame):
    numeric_df = df.select_dtypes(include="number")

    if numeric_df.empty:
        return px.imshow([[0]],title="<b>Feature Correlation Heatmap</b>")

    corr = numeric_df.corr()

    fig = px.imshow(
        corr,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="<b>Feature Correlation Heatmap</b>"
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Features",
        yaxis_title="Features",
        height=550
    )

    return fig