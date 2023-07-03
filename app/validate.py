# import pandas as pd
# import numpy as np

# def calculate_validation_results(source_data, target_data,col_to_remove = "Na"):
#     mismatched_columns = []
#     mismatched_data = []

#     # Find mismatched columns
#     mismatched_columns.append(col_to_remove)

#     source_data = source_data.replace(np.nan,'null')
#     target_data = target_data.replace(np.nan,'null')

#     for index, row in source_data.iterrows():
#         source_values = row.values
#         target_values = target_data.loc[index].values

#         if not all(source_values == target_values):
#             mismatched_data.append(dict(zip(source_data.columns, source_values)))
#     # Calculate other metrics
#     total_source_records = len(source_data)
#     total_target_records = len(target_data)

#     return {
#         "total_source_records": total_source_records,
#         "total_target_records": total_target_records,
#         "mismatched_columns": mismatched_columns,
#         "mismatched_data": mismatched_data[:10],
#     }


from dask.distributed import Client, LocalCluster
import dask.dataframe as dd


def handle_missing_values(data):
    """
    Handle missing values in the DataFrame by replacing them with default values.

    Args:
        data (dask.dataframe.DataFrame): Dask DataFrame.

    Returns:
        dask.dataframe.DataFrame: DataFrame with missing values replaced.
    """
    # Replace missing values in integer columns with 0
    int_columns = data.select_dtypes(include='integer').columns
    for column in int_columns:
        data[column] = data[column].fillna(0)

    # Replace missing values in object columns with an empty string
    object_columns = data.select_dtypes(include='object').columns
    for column in object_columns:
        data[column] = data[column].fillna('')
    
    # Replace missing values in object columns with an empty string
    float_columns = data.select_dtypes(include='float').columns
    for column in float_columns:
        data[column] = data[column].fillna(0.0)

    return data.reset_index()



# def calculate_validation_results(source_data, target_data, col_to_remove="Na"):
#     """
#     Calculate the validation results between source and target data using Dask.

#     Args:
#         source_data (dask.dataframe.DataFrame): Dask DataFrame representing the source data.
#         target_data (dask.dataframe.DataFrame): Dask DataFrame representing the target data.
#         col_to_remove (str): Column to remove.

#     Returns:
#         dict: Dictionary containing validation results.
#     """
#     mismatched_columns = []
#     mismatched_data = []

#     # Find mismatched columns
#     mismatched_columns.append(col_to_remove)

#     source_data = handle_missing_values(source_data)
#     target_data = handle_missing_values(target_data)


#     try:
#         # Set up a local Dask cluster
#         with LocalCluster() as cluster, Client(cluster) as client:
#             # Merge and iterate over rows of both DataFrames simultaneously
#             merged_data = dd.merge(
#                 source_data.reset_index(drop=True),
#                 target_data.reset_index(drop=True),
#                 left_index=True,
#                 right_index=True,
#                 suffixes=('_source', '_target')
#             )
#             for _, row in merged_data.iterrows():
#                 source_values = row[[
#                     col + '_source' for col in source_data.columns]].values
#                 target_values = row[[
#                     col + '_target' for col in target_data.columns]].values

#                 # Exclude columns with non-matching values from the comparison
#                 if not all(source_values == target_values):
#                     mismatched_data.append(
#                         {k: v for k, v in zip(
#                             source_data.columns, source_values) if k != 'index'}
#                     )

#         # Calculate other metrics
#         total_source_records = len(source_data)
#         total_target_records = len(target_data)

#         return {
#             "total_source_records": total_source_records,
#             "total_target_records": total_target_records,
#             "mismatched_columns": mismatched_columns,
#             "mismatched_data": mismatched_data[:10],
#         }
#     except Exception as e:
#         # Handle the exception appropriately
#         raise Exception("Error occurred during validation: " + str(e))

def calculate_validation_results(source_data, target_data, col_to_remove="Na"):
    """
    Calculate the validation results between source and target data using Dask.

    Args:
        source_data (dask.dataframe.DataFrame): Dask DataFrame representing the source data.
        target_data (dask.dataframe.DataFrame): Dask DataFrame representing the target data.
        col_to_remove (str): Column to remove.

    Returns:
        dict: Dictionary containing validation results.
    """
    mismatched_columns = []
    mismatched_data = []

    # Find mismatched columns
    mismatched_columns.append(col_to_remove)

    source_data = handle_missing_values(source_data)
    target_data = handle_missing_values(target_data)

    try:
        # Merge the DataFrames and compute the result
        merged_data = dd.merge(
            source_data.reset_index(drop=True),
            target_data.reset_index(drop=True),
            left_index=True,
            right_index=True,
            suffixes=('_source', '_target')
        ).compute()

        for _, row in merged_data.iterrows():
            source_values = row[[
                col + '_source' for col in source_data.columns]].values
            target_values = row[[
                col + '_target' for col in target_data.columns]].values

            # Exclude columns with non-matching values from the comparison
            if not all(source_values == target_values):
                mismatched_data.append(
                    {k: v for k, v in zip(
                        source_data.columns, source_values) if k != 'index'}
                )

        # Calculate other metrics
        total_source_records = len(source_data)
        total_target_records = len(target_data)

        return {
            "total_source_records": total_source_records,
            "total_target_records": total_target_records,
            "mismatched_columns": mismatched_columns,
            "mismatched_data": mismatched_data[:10],
        }
    except Exception as e:
        # Handle the exception appropriately
        raise Exception("Error occurred during validation: " + str(e))
