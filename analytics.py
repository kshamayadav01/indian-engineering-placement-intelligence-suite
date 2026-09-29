import pandas as pd 
import numpy as np
from database import run_query


def compute_future_projections():
    """
    computes marginal package returns across DSA tiers and projects
    future hiring inflation curves for technical profiles.
    """

    placed_df = run_query("""
        select DSA_problems_solved,package_LPA,collage_Tier,GitHub_Contributions
        from students
        WHERE placement_status = 'placed';
    """)

    # group DSA counts into step bins of 100
    bins = pd.cut(placed_df["DSA_problems_solved"], bins=range(0, 1200, 100))
    dsa_agg = placed_df.groupby(bins,observed= false)['package_LPA'].mean().reset_index
    dsa_agg['bin mid'] = [int(b.mid) for b in dsa_agg['DSA_problems_solved']]
    dsa_agg['projected_lpa'] = dsa_agg.dropna()

    # model projected skill premium curve (exponential compounding on technical milestones)
    dsa_agg['projected_lpa'] = dsa_agg['projected_lpa'] * (1+(dsa_agg['bin mid']/1000)* 0.35)

    # tier parity comparison by skill band
    placed_df['skill_band'] = pd.qcut(
        placed_df['DSA_problems_solved'],
        q=3,
        labels=['foundational(<120)','intermediate(120-240)','advanced(>240)']

    )
    tier_parity = placed_df.groupby(['skill_band','collage_Tier'],observed=False)['package_LPA'].mean().reset_index()  

    
    return {
        "dsa_curve": dsa_agg.to_dict(orient="records"),
        "tier_parity": tier_parity.to_dict(orient="records"),
        

    }        
                                