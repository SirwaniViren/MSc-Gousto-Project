import pandas as pd
import numpy as np
import os
from order_generator import OrderGenerator


class OrderAllocator:


    @staticmethod
    def allocate_orders(allocated_orders, allocated_order_eligibility, allocated_factory_caps):
        # Initialize columns
        allocated_orders['site'] = 'not_routed'
        allocated_order_eligibility['allocated'] = False

        # Iterate through each factory except the catch-all
        for factory in list(allocated_factory_caps.keys())[:-1]:
            cap = allocated_factory_caps[factory]

            # Get set S of unrouted orders eligible to the current factory
            eligible_orders = allocated_order_eligibility[(allocated_order_eligibility['allocated'] == False) &
                                                        (allocated_order_eligibility['eligibility'].apply(lambda i: factory in i))]

            if len(eligible_orders) < cap:
                raise ValueError(f'Not enough eligible orders for {factory}')
            else:
                for _ in range(cap):
                    if len(eligible_orders) == 0:
                        break
                    # Pick a random order from the eligible list
                    selected_order = eligible_orders.sample(1).iloc[0]
                    order_id = selected_order['order_id']

                    # Allocate items in allocated_orders
                    allocated_orders.loc[allocated_orders['order_id'] == order_id, 'site'] = factory

                    # Mark the order as allocated in allocated_order_eligibility
                    allocated_order_eligibility.loc[allocated_order_eligibility['order_id'] == order_id, 'allocated'] = True

                    # Update the eligible_orders to exclude the allocated order
                    eligible_orders = eligible_orders[eligible_orders['order_id'] != order_id]

        # Allocate remaining orders to catch-all
        catch_all_factory = list(allocated_factory_caps.keys())[-1]
        remaining_orders = allocated_order_eligibility[allocated_order_eligibility['allocated'] == False]
        for order_id in remaining_orders['order_id']:
            allocated_orders.loc[allocated_orders['order_id'] == order_id, 'site'] = catch_all_factory
            allocated_order_eligibility.loc[allocated_order_eligibility['order_id'] == order_id, 'allocated'] = True

        return allocated_orders
    


    @staticmethod
    def allocate_orders_gousto(allocated_orders, allocated_order_eligibility, factory_caps_dict):
        # Initialize columns
        allocated_orders['site'] = 'not_routed'
        allocated_order_eligibility['allocated'] = False

        # Iterate through each forecast_id
        for forecast_id in allocated_orders['forecast_id'].unique():
            print(forecast_id)
            # Extract factory caps for the current forecast_id
            allocated_factory_caps = factory_caps_dict.get(forecast_id, {})
            
            # Iterate through each factory except the catch-all
            for factory in list(allocated_factory_caps.keys())[:-1]:
                print(factory)
                cap = allocated_factory_caps[factory]
                # Get set S of unrouted orders eligible to the current factory
                eligible_orders = allocated_order_eligibility[
                    (allocated_order_eligibility['forecast_id'] == forecast_id) &
                    (allocated_order_eligibility['allocated'] == False) &
                    (allocated_order_eligibility['eligible_sites'].apply(lambda i: factory in i))
                ]

                if len(eligible_orders) < cap:
                    raise ValueError(f'Not enough eligible orders for {factory} in forecast_id {forecast_id}')
                else:
                    for i in range(cap):
                        print(i)
                        if len(eligible_orders) == 0:
                            break
                        # Pick a random order from the eligible list
                        selected_order = eligible_orders.sample(1).iloc[0]
                        order_id = selected_order['order_id']

                        # Allocate items in allocated_orders
                        allocated_orders.loc[
                            (allocated_orders['order_id'] == order_id) & 
                            (allocated_orders['forecast_id'] == forecast_id), 
                            'site'] = factory

                        # Mark the order as allocated in allocated_order_eligibility
                        allocated_order_eligibility.loc[
                            (allocated_order_eligibility['order_id'] == order_id) & 
                            (allocated_order_eligibility['forecast_id'] == forecast_id), 
                            'allocated'] = True

                        # Update the eligible_orders to exclude the allocated order
                        eligible_orders = eligible_orders[eligible_orders['order_id'] != order_id]

            # Allocate remaining orders to catch-all
            catch_all_factory = list(allocated_factory_caps.keys())[-1]
            remaining_orders = allocated_order_eligibility[
                (allocated_order_eligibility['forecast_id'] == forecast_id) &
                (allocated_order_eligibility['allocated'] == False)
            ]
            for order_id in remaining_orders['order_id']:
                allocated_orders.loc[
                    (allocated_orders['order_id'] == order_id) & 
                    (allocated_orders['forecast_id'] == forecast_id), 
                    'site'] = catch_all_factory
                allocated_order_eligibility.loc[
                    (allocated_order_eligibility['order_id'] == order_id) & 
                    (allocated_order_eligibility['forecast_id'] == forecast_id), 
                    'allocated'] = True

        return allocated_orders
        

if __name__ == "__main__":


    order_dir = 'orders_22'
    eligibility_dir = 'orders_eligibility_22'
    allocation_dir = 'allocations_22'

    # Load factory caps from a file
    factory_caps = OrderGenerator.load_factory_caps('factory_caps_22.json')

    # Create the allocations directory if it doesn't exist
    os.makedirs(allocation_dir, exist_ok=True)

    for lead_day in range(16, 0, -1):
        # Load the DataFrames
        orders_df = pd.read_csv(f'{order_dir}/orders_22_lead_day_{lead_day}.csv', low_memory=False)
        orders_eligibility_df = pd.read_csv(f'{eligibility_dir}/orders_eligibility_22_lead_day_{lead_day}.csv', low_memory=False)

        # Allocate orders
        allocated_orders_df = OrderAllocator.allocate_orders_gousto(orders_df.copy(), orders_eligibility_df.copy(), factory_caps.copy())

        # Save the allocation DataFrame
        allocated_orders_df.to_csv(f'{allocation_dir}/allocation_22_lead_day_{lead_day}.csv', index=False)

    print("Order allocations have been saved.")