#!/usr/bin/python3

from monday import monday
from database import database
from sort import sort

db              = database()
product_list    = db.get_List()
monday_instance = monday()
sort_instance   = sort()
product_list    = sort_instance.full_sort(product_list)

'''
Clears the planning and adds new products to monday
'''
print("Clearing Board")
monday_instance.clear_all()
print("Board Cleared")

print("Mutating")
for days in product_list["Days"]:
    for product in days["Products"]:
        monday_instance.mutate(product["Name"], product["Fill"], product["Fill_Time"], product["Priority"], days["Group"], product["Real_ID"])
print("Mutation Complete!")
