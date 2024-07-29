import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 


class WMAPE:

    @staticmethod
    def calculate_wmape_site(merged_df, soft_col, hard_col):
        total_forecast = merged_df["lead_0"].sum()
        site_df = merged_df.copy()
        site_df['abs_error'] = (site_df[soft_col] - site_df[hard_col]).abs()

        # Calculate WMAPE_site
        wmape_site = site_df["abs_error"].sum() / total_forecast

        return site_df, wmape_site
    

    @staticmethod
    def calculate_wmape_global(merged_df, soft_col, hard_col):
        total_forecast = merged_df["lead_0"].sum()
        global_df = merged_df.copy()
        global_df = global_df.groupby('item_id').sum().reset_index()
        global_df['abs_error'] = (global_df[soft_col] - global_df[hard_col]).abs()
        global_df = global_df.drop(['site'], axis=1, errors='ignore')

        # Calculate WMAPE_global
        wmape_global = global_df["abs_error"].sum() / total_forecast

        return global_df, wmape_global
    


if __name__ == "__main__":

    merged_dir = 'merged'
    
    # List of lead days
    lead_days = list(range(18, -1, -1))

    # Initialize lists to store WMAPE values
    wmape_site_values = []
    wmape_global_values = []

    # Loop through all lead days to calculate WMAPE
    for lead_day in lead_days:
        # Load the merged DataFrame
        merged_df = pd.read_csv(f'{merged_dir}/merged_lead_day_{lead_day}_0.csv')
        
        # Calculate WMAPE for site and global
        soft_col = f'lead_{lead_day}'
        hard_col = 'lead_0'
        
        if lead_day == 0:
            wmape_site = 0
            wmape_global = 0
        else:
            _, wmape_site = WMAPE.calculate_wmape_site(merged_df, soft_col, hard_col)
            _, wmape_global = WMAPE.calculate_wmape_global(merged_df, soft_col, hard_col)
        
        # Append the WMAPE values to the lists
        wmape_site_values.append(wmape_site)
        wmape_global_values.append(wmape_global)

    # Plot the data
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.plot(lead_days, wmape_site_values, linestyle='-', color='b', label="WMAPE Site")
    plt.plot(lead_days, wmape_global_values, linestyle='-', color='r', label="WMAPE Global")
    plt.xlabel('Lead Day')
    plt.ylabel('Error')
    plt.title('WMAPE Values for Different Lead Days')
    plt.xticks(lead_days, rotation=45)
    plt.legend()
    plt.gca().invert_xaxis()  # Invert x-axis to have 0 at the end
    plt.tight_layout()
    plt.savefig('wmape.png')
    plt.show()