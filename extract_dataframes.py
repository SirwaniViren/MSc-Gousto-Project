import pandas as pd
import numpy as np
import datetime as dt
import os
import json
import ast



def extract_save_factory_caps(site_data, lead_days):

    with open(site_data, 'r') as file:
        factory_caps_json = json.load(file)

    with open(lead_days, 'r') as file:
        lead_day_dict = json.load(file)
    
    factory_caps = {}
    
    for forecast_id, _ in lead_day_dict.items():
        if forecast_id in factory_caps_json:
            caps = {}
            for factory_name, factory_info in factory_caps_json[forecast_id]['site_info'].items():
                daily_caps = factory_info['daily_caps']
                if "2024/04/22" in daily_caps:
                    caps[factory_name] = str(daily_caps["2024/04/22"]) if daily_caps["2024/04/22"] == float('inf') else daily_caps["2024/04/22"]
            factory_caps[forecast_id] = caps
    
    factory_caps_filename = 'factory_caps_22.json'
    with open(factory_caps_filename, 'w') as file:
            json.dump(factory_caps, file)


def extract_eligibility(df_name, delivery_date):
    
    dtype_dict = {
    'order_id': str,
    'delivery_date': str,
    'order_items': str,
    'simulated': bool,
    'delivery_site_preference': str,
    'num_portions': int,
    'eligible_sites': list,
    'forecast_id': str
    }
    
    eligibility_df = pd.read_csv(df_name, low_memory=False)
    with open('forecast_id_22.json', 'r') as file:
        forecast_to_lead_days = json.load(file) 

    # Filter the dataframe based on the specified forecast_id and delivery_date
    filtered_df = eligibility_df[eligibility_df['delivery_date'] == delivery_date]

    # Convert simulated column to 'real' or 'simulated'
    filtered_df['order_type'] = filtered_df['simulated'].apply(lambda x: 'real' if not x else 'sim')
    
    # Create the final dataframe with only the required columns
    filtered_df['lead_day'] = filtered_df['forecast_id'].map(forecast_to_lead_days)
    orders_eligibility_df = filtered_df[['order_id', 'eligible_sites', 'order_type', 'lead_day', 'forecast_id']]

    orders_eligibility_name = 'orders_eligibility_22' + '.csv'
    orders_eligibility_df.to_csv(orders_eligibility_name, index=False)



def extract_save_orders_lead_days(filename, delivery_date):
    
    dtype_dict = {
    'order_id': str,
    'delivery_date': str,
    'itemable_type' : str,
    'item_id' : str,
    'num_portions': int,
    'quantity' : int,
    'forecast_id': str, 
    'menu_week': int,
    'forecast_created_tstamp': str,
    'created_tstamp': str,
    'site': str, 
    'state': str
}
    
    full_ssf_df = pd.read_csv(filename, dtype=dtype_dict, low_memory=False)
    ssf_df = full_ssf_df[full_ssf_df['delivery_date'] == delivery_date]

    # First, ensure that both datetime columns are tz-aware or tz-naive consistently
    ssf_df['delivery_date'] = pd.to_datetime(ssf_df['delivery_date']).dt.tz_localize(None)
    ssf_df['forecast_created_tstamp'] = pd.to_datetime(ssf_df['forecast_created_tstamp'], format='mixed', utc=True).dt.tz_localize(None)

    # Calculate the number of days between delivery_date and forecast_created_tstamp
    ssf_df['lead_days'] = (ssf_df['delivery_date'] - ssf_df['forecast_created_tstamp']).dt.days
    orders_name = 'orders_22.csv'
    ssf_df.to_csv(orders_name, index=False)
    return ssf_df


def create_order_df(filename):
     
     def determine_order_type(order_id):
        return 'simulated' if str(order_id).startswith('simulated') else 'real'
     
     orders_df = pd.read_csv(filename, low_memory=False)
     for i in range(0, 19):
          if i in orders_df['lead_days'].values:
               i_df = orders_df[orders_df['lead_days'] == i]
               i_df['order_type'] = i_df['order_id'].apply(determine_order_type)
               orders_i_df = i_df[['order_id', 'item_id', 'order_type', 'forecast_id']]
               orders_i_df.to_csv(f'orders_22/orders_22_lead_day_{i}.csv', index=False)


def extract_forecast_id(filename):
     
     orders_df = pd.read_csv(filename, low_memory=False)
     orders_df = orders_df.drop_duplicates(subset=['forecast_id', 'lead_days'])

     forecast_to_lead_day = orders_df.set_index('forecast_id')['lead_days'].to_dict()

     with open('forecast_id_22.json', 'w') as file:
            json.dump(forecast_to_lead_day, file)


def eligibile_sites_extract(filename):
    
    orders_eligibility_df = pd.read_csv(filename, low_memory=False)

    # Convert the string representation of lists to actual lists
    orders_eligibility_df['eligible_sites'] = orders_eligibility_df['eligible_sites'].apply(ast.literal_eval)

    # Group by lead_day and save each group to a separate file
    lead_days = orders_eligibility_df['lead_day'].unique()

    for lead_day in lead_days:
        lead_day_df = orders_eligibility_df[orders_eligibility_df['lead_day'] == lead_day]
        lead_day_df.to_csv(f'orders_eligibility_22/orders_eligibility_22_lead_day_{lead_day}.csv', index=False)


if __name__ == "__main__":
    
    # extract_save_factory_caps('multisite_config.json', 'forecast_id_22.json')
    # extract_eligibility('eligibility.csv', '2024-04-22')
    # extract_save_orders_lead_days('ssf.csv', '2024-04-22')
    # extract_forecast_id('orders_22.csv')
    # eligibile_sites_extract("orders_eligibility_22.csv")
    create_order_df('orders_22.csv')