import plotly.express as px
import pandas as pd


def build_granular_scatter(df: pd.DataFrame):
    """
    Renders an interactive scatter plot with rich multi-attribute tooltips.
    """

    fig = px.scatter(
        df,
        x="DSA_Problems_Solved",
        y="Package_LPA",
        color="College_Tier",
        size="GitHub_Contributions",
        size_max=18,
        opacity=0.75,
        color_discrete_map={
            "Tier-1": "#2b5c8f",
            "Tier-2": "#e26d5c",
            "Tier-3": "#38b000"
        },
        category_orders={"College_Tier": ["Tier-1", "Tier-2", "Tier-3"]},
        labels={
            "DSA_Problems_Solved": "DSA Problems Solved",
            "Package_LPA": "Package (LPA)",
            "College_Tier": "College Tier"
        }
    )

    custom_cols = [
        "Student_ID",
        "Branch",
        "CGPA",
        "GitHub_Contributions",
        "Internships_Count",
        "Competitive_Programming_Rating"
    ]

    fig.update_traces(
        customdata=df[custom_cols].values,
        hovertemplate=(
            "<b>Candidate ID:</b> %{customdata[0]}<br>"
            "<b>Branch:</b> %{customdata[1]} <b>Tier:</b> %{fullData.name}<br>"
            "<b>CGPA:</b> %{customdata[2]:.2f}<br>"
            "<b>DSA Solved:</b> %{x}<br>"
            "<b>GitHub Usage:</b> %{customdata[3]}<br>"
            "<b>Internships:</b> %{customdata[4]}<br>"
            "<b>CP Rating:</b> %{customdata[5]}<br>"
            "<b>Package:</b> ₹%{y:.2f} LPA"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        template="plotly_white",
        hovermode="closest",
        hoverlabel=dict(
            bgcolor="rgba(255, 255, 255, 0.95)",
            font_size=12,
            font_family="Roboto, sans-serif",
            bordercolor="#cccccc"
        ),
        xaxis=dict(
            title="<b>DSA Problems Solved</b>",
            gridcolor="#f0f0f0"
        ),
        yaxis=dict(
            title="<b>Package (LPA)</b>",
            gridcolor="#f0f0f0"
        ),
        legend=dict(
            title="<b>College Tier</b>",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig