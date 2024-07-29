import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import json
from order_generator import OrderGenerator


def plot_factory_capacities(allocated_orders_df, factory_caps, lead_day):
    # Aggregate the orders by site and type
    real_orders_agg = allocated_orders_df[allocated_orders_df['order_type'] == 'real'].groupby('site')['order_id'].nunique()
    simulated_orders_agg = allocated_orders_df[allocated_orders_df['order_type'] == 'simulated'].groupby('site')['order_id'].nunique()

    # Ensure all sites are included in the aggregation and in the correct order
    all_sites = list(factory_caps.keys())
    real_orders_agg = real_orders_agg.reindex(all_sites, fill_value=0)
    simulated_orders_agg = simulated_orders_agg.reindex(all_sites, fill_value=0)

    # Prepare data for plotting
    sites = all_sites
    real_volumes = real_orders_agg[sites].values
    simulated_volumes = simulated_orders_agg[sites].values
    capacities = [factory_caps[site] if site in factory_caps else 0 for site in sites]

    # Plot the data
    fig, ax = plt.subplots(figsize=(15, 9))
    bar_width = 0.6

    bars_real = ax.bar(sites, real_volumes, bar_width, color='blue', label='Real Orders')
    bars_simulated = ax.bar(sites, simulated_volumes, bar_width, bottom=real_volumes, color='orange', label='Simulated Orders')

    # Add capacity lines and labels
    for site, cap in zip(sites, capacities):
        if cap == float('inf'):
            cap_label = 'inf'
        else:
            cap_label = str(cap)
            ax.plot([site, site], [0, cap], color='red', linestyle='--')
            ax.text(site, cap, cap_label, ha='center', va='bottom', color='red')

    ax.set_xlabel('Factories')
    ax.set_ylabel('Number of Orders')
    ax.set_title(f'Factory Capacities - Lead Day {lead_day}')
    ax.legend()

    plt.show()


def split_order_type(df):
    real_orders = df[df['order_type'] == 'real']['order_id'].nunique()
    simulated_orders = df[df['order_type'] == 'simulated']['order_id'].nunique()
    return real_orders, simulated_orders


if __name__ == "__main__":

    # Define directories
    order_dir = 'order_dataframes'
    eligibility_dir = 'order_eligibility_dataframes'
    allocation_dir = 'allocations'
    merged_dir = 'merged'

    # Load factory caps from a file
    factory_caps = OrderGenerator.load_factory_caps('factory_caps.json')

###########################################################################################################################################
###########################################################################################################################################

    # Plot for lead days 18, 12, 6, and 0
    lead_days = [18, 12, 6, 0]

    for lead_day in lead_days:
        # Load the allocated orders DataFrame
        allocated_orders_df = pd.read_csv(f'{allocation_dir}/allocation_lead_day_{lead_day}.csv')

        # Plot the factory capacities
        plot_factory_capacities(allocated_orders_df.copy(), factory_caps.copy(), lead_day)

    print("Plots have been generated.")

###########################################################################################################################################
###########################################################################################################################################

    # List of lead days
    lead_days = list(range(18, -1, -1))

    # Initialize lists to store aggregated data
    real_orders = []
    simulated_orders = []
    lead_day_labels = []

    # Loop through all lead days
    for lead_day in lead_days:
        # Load the allocated orders DataFrame
        allocated_orders_df = pd.read_csv(f'{allocation_dir}/allocation_lead_day_{lead_day}.csv')
        
        # Aggregate data
        real_orders_count, simulated_orders_count = split_order_type(allocated_orders_df.copy())
        real_orders.append(real_orders_count)
        simulated_orders.append(simulated_orders_count)
        lead_day_labels.append(f'-{lead_day} days' if lead_day != 0 else 'Delivery date')

    # Plot the data
    fig, ax = plt.subplots(figsize=(15, 9))

    bar_width = 0.6
    bars_real = ax.bar(lead_day_labels, real_orders, bar_width, color='blue', label='Real Orders')
    bars_simulated = ax.bar(lead_day_labels, simulated_orders, bar_width, bottom=real_orders, color='orange', label='Simulated Orders')

    # Add labels and title
    ax.set_xlabel('Lead Day')
    ax.set_ylabel('Number of Orders')
    ax.set_title('Orders Allocated per Lead Day')
    ax.legend()

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('allocated_orders_per_day.png')
    plt.show()