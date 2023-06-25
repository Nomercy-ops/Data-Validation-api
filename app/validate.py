import pandas as pd

def calculate_validation_results(source_data, target_data,col_to_remove = "Na"):
    mismatched_columns = []
    mismatched_data = []

    # Find mismatched columns
    mismatched_columns.append(col_to_remove)

    for index, row in source_data.iterrows():
        source_values = row.values
        target_values = target_data.loc[index].values

        if not all(source_values == target_values):
            mismatched_data.append(dict(zip(source_data.columns, source_values)))
    # Calculate other metrics
    total_source_records = len(source_data)
    total_target_records = len(target_data)
    
    return {
        "total_source_records": total_source_records,
        "total_target_records": total_target_records,
        "mismatched_columns": mismatched_columns,
        "mismatched_data": mismatched_data[:10],
    }
