#!/usr/bin/python3

from monday import monday
from datetime import date
from database import database
from sort import sort


db              = database()
product_list    = db.get_List()
monday_instance = monday()
sort_instance   = sort()
product_list    = sort_instance.full_sort(product_list)
today           = date.today().weekday()
groups          = []

print("Moving")

for group in product_list["Days"]:
    groups.append(group["Group"]) 
    
'''
Moves uncompleted task from days before to today
'''
monday_instance.move(today, groups)

print("Move Completed")
