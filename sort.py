class sort:
    def __init__(self):
        self.groups = {
            # The groups ids in monday can be different
            "Days" : [
                { # Monday
                    "Name"       : "Monday",
                    "Group"      : "topics",
                    "Total_Time" : 0,
                    "Products"   : list()
                },
                { # Tuesday
                    "Name"       : "Tuesday",
                    "Group"      : "group_title",
                    "Total_Time" : 0,
                    "Products"   : list()
                },
                { # Wednesday
                    "Name"       : "Wednesday",
                    "Group"      : "nieuwe_groep",
                    "Total_Time" : 0,
                    "Products"   : list()
                },
                { # Thursday
                    "Name"       : "Thursday",
                    "Group"      : "nieuwe_groep69700",
                    "Total_Time" : 0,
                    "Products"   : list()
                },
                { # Friday
                    "Name"       : "Friday",
                    "Group"      : "nieuwe_groep51929",
                    "Total_Time" : 0,
                    "Products"   : list()
                }
            ]
        }

    def full_sort(self, product_list):
        '''
        Sorts de list with products

        Parameters:
            product_list (list): A list with dictionaries 
        '''

        self.product_list = product_list

        for product in self.product_list:
            product["Days_Left"] = self.days_left(product["Stock"], product["Optimal"])
            product["Priority"] = self.priority(product)

        self.sorted_list = self.bubble_sort(self.product_list, "Days_Left")
        self.sorted_list = self.bubble_sort(self.sorted_list, "Fill_Time", reverse=True)
        self.product_distribution()
        self.swap()
         
        return self.groups
        
    def days_left(self, stock, optimal):
        '''
        Calculates how many days are left until there is 0 in stock

        Parameters:
            stock (int): Current stock
            optimal (int): Optimal ammount
        '''
        sold_per_day = optimal / 28
        sum = stock / sold_per_day
        return sum

    def bubble_sort(self, array, key, reverse=False):
        '''
        Uses the bubble sorting algorithm to sort

        Parameters:
            array (list): A list with dictionaries items
            key (string): Wich value to sort by
            reverse (bool, optional): Wether to sort the array in ascending(default) or descending order
        '''
        n = len(array)

        for i in range(n):
            already_sorted = True

            for j in range(n - i - 1):
                value1 = float(array[j][key])
                value2 = float(array[j + 1][key])
                if reverse:
                    if value1 < value2:
                        array[j], array[j + 1] = array[j + 1], array[j]
                        already_sorted = False
                else:
                    if value1 > value2:
                        array[j], array[j + 1] = array[j + 1], array[j]
                        already_sorted = False

            if already_sorted:
                break

        return array
    
    def priority(self, product):
        '''
        Returns the priority for the product based on how many days until the stock is empty

        Parameters:
        product (dict): A product with a key("Days_Left")
        '''
        if product["Days_Left"] <= 1:
            priority = "Critical"
        elif product["Days_Left"] > 1 and product["Days_Left"] <= 10:
            priority = "High"
        elif product["Days_Left"] > 10 and product["Days_Left"] <= 20:
            priority = "Medium" 
        elif product["Days_Left"] > 20:
            priority = "Low"
        return priority
    
    def day_distribution(self):
        '''
        Calculates the distribution of products across five days based on the number of products.
        
        Example:
        If there are 19 products the distribution returns [4, 4, 4, 4, 3]
        '''
        days = [0, 0, 0, 0, 0]
        ammount = len(self.product_list)
        num     = ammount - ammount % (len(days))
        module  = ammount % len(days)

        for i in range(module):
            days[i] += 1

        for i in range(len(days)):
            days[i] += int(num / len(days))
            if i > 0:
                days[i] += days[i - 1]

        return days

    def product_distribution(self):
        '''
        Distributes products across days based on the day distribution
        '''
        days = self.day_distribution()
        for i in range(len(days)):
            begin = days[i - 1] if i > 0 else 0
            for j in range(begin, days[i]):
                self.groups["Days"][i]["Products"].append(self.product_list[j])
        
    def time_check(self, days):
        '''
        Checks if the total time of each day is bigger than 960 min. 
        
        returns True if it's bigger
        returns False if it's smaller
        '''
        over_time = False
        for day in days:
            time = 0
            for product in day["Products"]:
                time += float(product["Fill_Time"])
            day["Total_Time"] = time
            if time > 960:
                over_time = True
        return over_time

    def swap(self):
        '''
        Swaps products around untill each day has less than 960 min total time
        '''
        x = 0
        while self.time_check(self.groups["Days"]) and x < 100:
            for i in range(len(self.groups["Days"])):
                if self.groups["Days"][i]["Total_Time"] > 960:
                    for j in range(len(self.groups["Days"][i]["Products"])):
                        for l in range(len(self.groups["Days"])):
                            for k in range(len(self.groups["Days"][l]["Products"])):
                                temp_prod                             = self.groups["Days"][i]["Products"][j]
                                self.groups["Days"][i]["Products"][j] = self.groups["Days"][l]["Products"][k]
                                self.groups["Days"][l]["Products"][k] = temp_prod
            x += 1

    def get_groups(self):
        return self.groups        
