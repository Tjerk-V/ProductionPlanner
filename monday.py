import requests
import json
import time

apiKey  = ""
apiUrl  = "https://api.monday.com/v2"
headers = {"Authorization" : apiKey}

class monday:
    def mutate(self, prod_name, fill, time, priority, group, real_id):
        '''
        Adds a product to monday.com 

        Parameters:
            prod_name (string): Product name
            fill (int): Fill ammount
            time (float): Fill lenght
            priority (string): The priority of the product
            group (string): Group ID
            real_id (int): The real ID of the product
        '''
        vars = {
            'myItemName' : prod_name,
            'columnVals' : json.dumps({
            'status'     : "Niet begonnen",
            'nummers'    : fill,
            'nummers0'   : time,
            'priority'   : priority,
            'nummers1'   : real_id
            })
        }
        query = 'mutation ($myItemName: String!, $columnVals: JSON!) { create_item (board_id:1222490166, group_id:'+ group +' item_name:$myItemName, column_values:$columnVals) { id } }'
        
        data = {'query' : query, "variables": vars}
        self.get_data(data)
    
    def retrieve(self):
        '''
        Returns the value of each column with the type text
        '''
        query = '''
        { boards (limit:50) {
        items {
        id
            column_values{
            text
        } } } }
        '''

        data = {'query' : query}
        self.get_data(data)
        return self.returned_data
    
    def move(self, weekday, groups):
        '''
        Moves items from one group to another.

        Parameters:
        weekday (int): Current day
        groups (list): A list of group id's from monday
        '''
        
        query = '''
        { boards (limit:40) {
        items {
        id
            column_values{
                text
            }
            group{
                title
        } } } } 
        '''
        data = {"query" : query}
        self.get_data(data)
        
        group_id  = groups[weekday]
        all_days  = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag"]
        past_days = []

        for i in range(weekday):
            past_days.append(all_days[i])

        for item in self.returned_data["data"]["boards"][1]["items"]:
            id     = item["id"]
            group  = item["group"]["title"]
            status = item["column_values"][1]["text"]

            for day in past_days:
                if day.lower() in group.lower() and status == "Niet begonnen":
                    query = 'mutation { move_item_to_group (item_id: '+ id +', group_id: '+ group_id +') { id } }'
                    data  = {'query' : query}
                    self.get_data(data)

        print("Products moved to", groups[weekday])
    
    def clear_all(self):
        '''
        Removes every item from monday
        '''
        query = '''
        { boards (limit:50) {
        items{
        id
        } } }
        '''
        data = {'query' : query}
        
        self.get_data(data)

        for item in self.returned_data["data"]["boards"][1]["items"]:
            query = ' mutation { delete_item (item_id: '+ item["id"] +') { id }} '
            data = {'query' : query}
            self.get_data(data)

    def get_board_data(self):
        '''
        Returns the items and groups from monday
        '''
        query = '''
        { boards (limit:50) {
        name
        id
        description
        items {
            name
            id
            column_values {
            title
            id
            type
            text
            }
        }
        groups{
        id
        title
        } } } 
        '''

        data = {'query' : query}
        self.get_data(data)
        return self.returned_data
    
    def get_item_ids(self):
        '''
        Returns a list with item ids from monday and with their real id
        '''
        query = ''' {
        boards (limit: 50) {
        items{
        column_values{
        text 
        }
        id
        } } }
        '''
        data = {'query' : query}
        self.get_data(data)
        items = []
        for item in self.returned_data["data"]["boards"][1]["items"]:
            new_dict = {
                "Item_ID": item["id"],
                "Real_ID": item["column_values"][6]["text"]
            }
            items.append(new_dict)
        return items
    
    def get_item_activity(self, item_id):
        '''
        Returns the product fill time or None

        Parameters:
        item_id (int): An id of a product from monday
        '''
        query = '''{
        boards (ids: 1222490166) {
            activity_logs(item_ids: '''+str(item_id)+''') {
            data
            event
            created_at 
            } } }'''
        
        data = {'query' : query}
        self.get_data(data)
        previous_value = ""
       
        #function
        for activity in self.returned_data["data"]["boards"][0]["activity_logs"]:
            event = activity["event"]
            data = activity["data"]
            #function
            if event == "update_column_value":
                if '"text":"Ermee bezig"' in data and previous_value == "Klaar":
                    st_time = activity["created_at"]
                    final_time = (int(en_time) - int(st_time)) / 600000000
                    return final_time
                elif '"text":"Niet begonnen"' in data or event == "create_pulse"  and previous_value == "Klaar":
                    return 0
                elif '"text":"Klaar"' in data:
                    previous_value = "Klaar"
                    en_time = activity["created_at"]
                elif '"text":"Niet begonnen"' in data:
                    previous_value = "Niet begonnen"
                elif '"text":"Ermee bezig"' in data:
                    previous_value = "Ermee bezig"
        return None   

    def remove_item(self, item_id):
        '''
        Removes one item from monday
        '''
        query = ' mutation { delete_item (item_id: '+ item_id +') { id }} '
        data = {'query' : query}
        self.get_data(data)

    def get_data(self, data):
        '''
        Attemps to return data from monday
        '''
        x = 0
        while True:
            r = requests.post(url=apiUrl, json=data, headers=headers)
            self.returned_data = r.json()
            try:
                self.returned_data["data"]
                return
            except:
                msg = str(self.returned_data["error_message"])
                cost = int(msg.split("cost")[1].split("budget")[0])
                if cost >= 1000000:
                    print("The query cost is too big. Try lowering the board limit")
                    return
                
                x += 1
                if x >= 61:
                    print("Couldn't connect with the board")
                time.sleep(1) 
