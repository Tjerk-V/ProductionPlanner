#!/usr/bin/python3

from monday import monday
from database import database
from sort import sort

db              = database()
monday_instance = monday()
sort_instance   = sort()
product_list    = db.get_List()
product_list    = sort_instance.full_sort(product_list)
items           = monday_instance.get_item_ids()

'''
Tries to retrieve the final time from an item and dumps it into the database
'''
print("Pulling")

for item in items:
    final_time = monday_instance.get_item_activity(item["Item_ID"])
    if final_time != None:
        for day in product_list["Days"]:
            for product in day["Products"]:
                if product["Real_ID"] == int(item["Real_ID"]):
                    monday_instance.remove_item(item["Item_ID"])
                    print(product["Fill"])
                    if int(product["Fill"]) == 0 or final_time == 0:
                        continue
                    else: 
                        final_time /= int(product["Fill"])
                        db.dump_fill_time(product["Real_ID"], product["Batch"], float(final_time))
    else:
        continue
    
print("Pull Completed")
