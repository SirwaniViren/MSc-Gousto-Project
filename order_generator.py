import pandas as pd
import random
import os
import json

class OrderGenerator:

    @staticmethod
    def create_eligibility_dict(num_factories, num_items):
        items = list(range(100, 100 + num_items * 10, 10))
        eligibility_dict = {}

        # Start with a base number of items for the first factory
        num_eligible_items = random.randint(5, 15)

        for i in range(1, num_factories + 1):
            if i == num_factories:
                # Last factory gets all items
                eligibility_dict[f"F{i}"] = items
            else:
                eligibility_dict[f"F{i}"] = items[:num_eligible_items]
                # Randomly determine the number of additional items for the next factory
                num_eligible_items += random.randint(1, 10)
                # Ensure num_eligible_items does not exceed the total number of items
                num_eligible_items = min(num_eligible_items, num_items)

        return eligibility_dict


    @staticmethod
    def create_factory_caps(num_factory, max_boxes):
        factory_caps = {}
        # Start with an initial capacity for the first factory
        cap = random.randint(1, max_boxes // 10)  # Starting with a base capacity

        for i in range(1, num_factory + 1):
            if i == num_factory:
                # Last factory gets infinite capacity
                factory_caps[f"F{i}"] = float('inf')
            else:
                factory_caps[f"F{i}"] = cap
                # Randomly increase the capacity for the next factory
                cap += random.randint(1, max_boxes // 10)
                # Ensure the capacity does not exceed max_boxes
                cap = min(cap, max_boxes)

        return factory_caps
    

    @staticmethod
    def save_factory_caps(factory_caps, filename):
        with open(filename, 'w') as file:
            json.dump(factory_caps, file)

    
    @staticmethod
    def load_factory_caps(filename):
        with open(filename, 'r') as file:
            factory_caps = json.load(file)
        return factory_caps


    @staticmethod
    def generate_total_boxes(factory_caps, min_extra_boxes, max_extra_boxes, lead_day):
        # Calculate total capacity excluding the infinite capacity
        finite_capacity = sum(cap for cap in factory_caps.values() if cap != float('inf'))

        # Add a random number of extra boxes to exceed the total capacity
        extra_boxes = random.randint(min_extra_boxes, max_extra_boxes)
        total_boxes = finite_capacity + extra_boxes

        # Determine the proportion of simulated orders based on the lead day
        if lead_day == 0:
            simulated_order_percentage = 0
        else:
            # Simulate orders percentage decreases linearly with lead day
            simulated_order_percentage = max(0, min(100, (lead_day / 18) * 100))

        # Calculate number of real and simulated orders
        num_simulated_orders = int(total_boxes * simulated_order_percentage / 100)
        num_real_orders = total_boxes - num_simulated_orders

        return num_real_orders, num_simulated_orders


    @staticmethod
    def generate_order_list(start_order_id, order_count, order_type, items, max_items_per_order=5):
        orders = []
        order_id = start_order_id

        while order_count > 0:
            num_items_in_order = min(random.randint(1, max_items_per_order), len(items))
            order_items = random.sample(items, num_items_in_order)
            for item in order_items:
                orders.append({'order_id': order_id, 'item_id': item, 'order_type': order_type})
            order_count -= 1
            order_id += 1

        return orders, order_id
    
    
    @staticmethod
    def generate_orders(total_real_orders, total_simulated_orders, num_items, max_items_per_order=5):
        items = list(range(100, 100 + num_items * 10, 10))
        current_order_id = 1

        # Generate real orders
        real_orders, current_order_id = OrderGenerator.generate_order_list(current_order_id, total_real_orders, 'real', items, max_items_per_order)

        # Generate simulated orders
        simulated_orders, _ = OrderGenerator.generate_order_list(current_order_id, total_simulated_orders, 'simulated', items, max_items_per_order)

        # Combine real and simulated orders
        all_orders = real_orders + simulated_orders

        # Convert to DataFrame
        orders_df = pd.DataFrame(all_orders)
        return orders_df
    

    @staticmethod
    def compute_orders_eligibility(orders_df, eligibility_dict):
        orders_eligibility = []

        for order_id in orders_df['order_id'].unique():
            order_items = orders_df[orders_df['order_id'] == order_id]['item_id'].tolist()
            order_type = orders_df[orders_df['order_id'] == order_id]['order_type'].iloc[0]
            eligible_factories = []
            for factory, items in eligibility_dict.items():
                if all(item in items for item in order_items):
                    eligible_factories.append(factory)
            orders_eligibility.append({'order_id': order_id, 'eligibility': eligible_factories, 'order_type': order_type})

        orders_eligibility_df = pd.DataFrame(orders_eligibility)
        return orders_eligibility_df
    
    


if __name__ == "__main__":

    # Define directories
    order_dir = 'order_dataframes'
    eligibility_dir = 'order_eligibility_dataframes'
    allocation_dir = 'allocations'

    # Create directories if they don't exist
    os.makedirs(order_dir, exist_ok=True)
    os.makedirs(eligibility_dir, exist_ok=True)

    # Create the allocations directory if it doesn't exist
    os.makedirs(allocation_dir, exist_ok=True)

    # Define factory caps and eligibility dictionary
    num_factories = 20
    num_items = 100
    factory_caps = OrderGenerator.create_factory_caps(num_factories, 100)
    OrderGenerator.save_factory_caps(factory_caps, 'factory_caps.json')
    eligibility_dict = OrderGenerator.create_eligibility_dict(num_factories, num_items)

    # Loop through lead days from 18 to 0
    for lead_day in range(18, -1, -1):
        num_real_orders, num_simulated_orders = OrderGenerator.generate_total_boxes(factory_caps, 1000, 2000, lead_day)
        orders_df = OrderGenerator.generate_orders(num_real_orders, num_simulated_orders, num_items)
        orders_eligibility_df = OrderGenerator.compute_orders_eligibility(orders_df, eligibility_dict)

        # Save DataFrames to files
        orders_df.to_csv(f'{order_dir}/orders_lead_day_{lead_day}.csv', index=False)
        orders_eligibility_df.to_csv(f'{eligibility_dir}/orders_eligibility_lead_day_{lead_day}.csv', index=False)

 
    print("Order DataFrames and Order Eligibility DataFrames have been saved.")
            
            