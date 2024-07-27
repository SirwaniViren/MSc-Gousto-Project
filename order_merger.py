import pandas as pd
import numpy as np
import os


class OrderMerger:


    @staticmethod
    def aggregate_items(allocated_orders_df, day):
        lead_day = 'lead_' + str(day)
        aggregated_df = allocated_orders_df.groupby(['item_id', 'site']).size().reset_index(name=lead_day)
        return aggregated_df


    @staticmethod
    def merge_allocation(soft_df, hard_df, soft_num, hard_num):
        soft_day = 'lead_' + str(soft_num)
        hard_day = 'lead_' + str(hard_num)

        # Merge the two dataframes on 'item_id' and 'site'
        merged_df = pd.merge(soft_df, hard_df, on=['item_id', 'site'], how='outer')

        # Fill NaN values with zeros
        merged_df.fillna(0, inplace=True)

        # Ensure the integer type for lead_day columns
        if soft_day in merged_df.columns:
            merged_df[soft_day] = merged_df[soft_day].astype(int)
        else:
            merged_df[soft_day] = 0  # Add the column if it doesn't exist

        if hard_day in merged_df.columns:
            merged_df[hard_day] = merged_df[hard_day].astype(int)
        else:
            merged_df[hard_day] = 0  # Add the column if it doesn't exist

        return merged_df
    

if __name__ == "__main__":

    # Define directories
    order_dir = 'order_dataframes'
    eligibility_dir = 'order_eligibility_dataframes'
    allocation_dir = 'allocations'
    merged_dir = 'merged'

    # Create the merged directory if it doesn't exist
    os.makedirs(merged_dir, exist_ok=True)

    # List of lead days
    lead_days = list(range(18, -1, -1))

    # Load and aggregate the hard allocation for lead day 0
    allocation_0 = pd.read_csv(f'{allocation_dir}/allocation_lead_day_0.csv')
    aggregated_0 = OrderMerger.aggregate_items(allocation_0, 0)

    # Loop through all lead days to aggregate and merge
    for lead_day in lead_days:
        # Load the allocated orders DataFrame
        allocation_df = pd.read_csv(f'{allocation_dir}/allocation_lead_day_{lead_day}.csv')
        
        # Aggregate the items
        aggregated_df = OrderMerger.aggregate_items(allocation_df, lead_day)
        
        # Merge with the hard allocation for lead day 0
        merged_df = OrderMerger.merge_allocation(aggregated_df, aggregated_0, soft_num=lead_day, hard_num=0)
        
        # Save the merged DataFrame
        merged_df.to_csv(f'{merged_dir}/merged_lead_day_{lead_day}_0.csv', index=False)

    print("Merged DataFrames have been saved.")