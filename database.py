import os
import pandas as pd
from sqlalchemy import create_engine,text

# --- configure your mysql workbench credentials ---
DB_USER ="root"
DB_PASSWORD= "admin" 
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "campus_db"
CSV_PATH = r"C:\Users\prade\OneDrive\Desktop\python_sql_project\indian_engineering_placement_2026.csv"

DEFAULT_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"
DATABASE_URL = f"{DEFAULT_DATABASE_URL}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

def ensure_database() -> None:
    """create the target databaase if it does not exist"""
    default_engine = create_engine(DEFAULT_DATABASE_URL)
    with default_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`"))
    default_engine.dispose()

    global engine
    engine = create_engine(DATABASE_URL)


def init_db(csv_path: str = CSV_PATH):
    """
    cleans raw csv  data,imputes nulls, and streams into MYSQL.
    """

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"source file '{csv_path}' was not found.")

    ensure_database()
    df= pd.read_csv(csv_path)


    # imputes missing values with medians
    if "open_source_contributions" in df.columns:
        df["open_source_contributions"] = df["open_source_contributions"].fillna(
            df["open_source_contributions"].median()
        )
    if "Linkedin_Activity_Score" in df.columns:
        df["Linkedin_Activity_Score"] = df["Linkedin_Activity_Score"].fillna(
            df["Linkedin_Activity_Score"].median()
        )

    # stream into mysql
    df.to_sql("students",con=engine,if_exists = "replace",index=False)

    # create engine in mysql using a safe prefix length for string columns.
    with engine.connect() as conn:
        conn.execute(text("alter table students add index idx_tier(college_tier(50));"))
        conn.execute(text("alter table students add index idx_branch (branch(50));"))
        conn.execute(text("alter table students add index idx_placement (placement_status(20));"))
        conn.execute(text("alter table students add index idx_cgpa (CGPA);"))
        conn.execute(text("alter table students add index idx_dsa (DSA_problems_solved);"))
        conn.commit()

    print("data successfully loaded and indexed in MySql Workbench")    


def run_query(query:str,params:tuple=()) -> pd.DataFrame:
    """runs queries against mysql using sqlalchemy.engine
    """
    with engine.connect()as conn:
        return pd.read_sql_query(text(query),conn,params=params)


if __name__ == "__main__":
    init_db() 
    



    