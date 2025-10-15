"""Run basic Great Expectations checks on price_history table."""

import os
import sys
import pandas as pd
from sqlalchemy import create_engine
import json
from great_expectations.dataset import PandasDataset

def main():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not set.")
        sys.exit(1)

    suite_path = os.path.join(os.path.dirname(__file__), "dq_suite.json")
    with open(suite_path, "r") as f:
        suite = json.load(f)

    engine = create_engine(db_url)
    df = pd.read_sql("select * from price_history", engine)
    dataset = PandasDataset(df)

    all_passed = True
    for exp in suite["expectations"]:
        etype = exp["expectation_type"]
        kwargs = exp["kwargs"]
        func = getattr(dataset, etype, None)
        if not func:
            print(f"Unknown expectation: {etype}")
            continue
        result = func(**kwargs)
        success = result.get("success", False)
        print(f"{etype} ({kwargs}) -> {'PASS' if success else 'FAIL'}")
        if not success:
            all_passed = False

    if not all_passed:
        print("Data quality checks failed.")
        sys.exit(1)
    else:
        print("All data quality checks passed.")

if __name__ == "__main__":
    main()
