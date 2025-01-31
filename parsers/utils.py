import os
import pandas as pd


def export_to_csv(products):
    new_data = pd.DataFrame(products)
    if os.path.exists("dataset/table.csv"):
        existing_data = pd.read_csv("dataset/table.csv")
        updated_data = pd.concat([existing_data, new_data], ignore_index=True)
    else:
        updated_data = new_data
    updated_data.to_csv("dataset/table.csv", index=False)
