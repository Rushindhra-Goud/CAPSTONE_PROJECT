"""
Loads cleaned_accidents.csv into the accidents table.
This is the EXACT file Member 2 trained the model on -- do not swap in a
different version without re-checking the model's expected columns.

Run this once (and again any time the CSV is updated) with:
    python load_data.py
"""
import pandas as pd
from database import engine, Base, SessionLocal
from models.accident import Accident

CSV_PATH = "cleaned_accidents.csv"  # place the CSV in this same folder


def load():
    Base.metadata.create_all(bind=engine)  # creates the table if it doesn't exist

    df = pd.read_csv(CSV_PATH)
    df = df.where(pd.notnull(df), None)  # convert NaN -> None for DB insert

    db = SessionLocal()
    try:
        db.query(Accident).delete()  # avoid duplicates on re-run

        records = df.to_dict(orient="records")
        db.bulk_insert_mappings(Accident, records)
        db.commit()
        print(f"Loaded {len(records)} accident records into the database.")
    finally:
        db.close()


if __name__ == "__main__":
    load()
