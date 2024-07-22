import pandas as pd
import random
import os
import matplotlib.pyplot as plt

class Order:
    def __init__(self, order_id, item_id, order_type, site=None):
        self.order_id = order_id
        self.item_id = item_id
        self.order_type = order_type
        self.site = site

    