#!/usr/bin/python3

from database import database
from monday import monday
from sort import sort
from datetime import date

db              = database()
monday_instance = monday()
sort_instance   = sort()
product_list    = db.get_List()
today           = date.today().weekday()
items           = monday_instance.get_item_ids()
items_real_id   = []
groups          = []

'''
Checks if the product is already in monday otherwise it'll add to product to today
'''
print("Updating board")

for group in sort_instance.get_groups()["Days"]:
    groups.append(group["Group"]) 

for item in items:
    items_real_id.append(int(item['Real_ID']))
for product in product_list:
    if int(product["Real_ID"]) in items_real_id:
        continue
    else:
        product["Days_Left"] = sort_instance.days_left(product["Stock"], product["Optimal"])
        product["Priority"] = sort_instance.priority(product)
        
        monday_instance.mutate(product["Name"], product["Fill"], product["Fill_Time"], product["Priority"], groups[today] ,product["Real_ID"])
        print("Added", product["Name"])

print("Update Completed")
