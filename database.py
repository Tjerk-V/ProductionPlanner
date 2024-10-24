import mysql.connector
import math

class database:
    def __init__(self):
        self.mydb = mysql.connector.connect(
            host="",
            user="",
            passwd="",
            database=""
            )
        

    def get_List(self):
        '''
        Connects to the database and returns a list with products 
        '''
                            #0         #1                    #2                        #3                                                                          #4           #5                                 #6                                     #7                #8        #9            #10       
        query  = ("SELECT vd.name, pp.description, rp.quantity_in_wmm_stock, rp.optimal_stock_quantity, (rp.optimal_stock_quantity - rp.quantity_in_wmm_stock) AS vullen, rp.wip_source_quantity, rp.wip_source_quantity_unit_fill_minutes, rp.wip_source_quantity_unit, rp.weight,rp.volume, rp.real_product_id FROM real_products rp LEFT JOIN virtual_product_descriptions vd ON rp.virtual_product_id = vd.virtual_product_id AND vd.language_id = 1 LEFT JOIN (SELECT rv.real_product_id, GROUP_CONCAT(pvd.value SEPARATOR ', ') AS DESCRIPTION FROM real_product_property_values rv JOIN property_value_descriptions pvd ON rv.property_value_id = pvd.property_value_id WHERE rv.real_product_id NOT IN (11804,11869,21208) AND pvd.language_id = 1 GROUP BY rv.real_product_id) AS pp ON rp.real_product_id = pp.real_product_id WHERE rp.virtual_product_id IN (SELECT rp.virtual_product_id FROM real_products rp WHERE rp.manufacturer_id IN (528,4,14, 2122) AND (rp.optimal_stock_quantity/4) > rp.quantity_in_wmm_stock  AND optimal_stock_quantity > 0 AND rp.real_product_id NOT IN  ( SELECT convertable_real_product_id  FROM real_product_conversions ) ) AND rp.real_product_id NOT IN  ( SELECT convertable_real_product_id  FROM real_product_conversions )AND rp.optimal_stock_quantity > 0 ORDER BY rp.virtual_product_id, (rp.optimal_stock_quantity - rp.quantity_in_wmm_stock) DESC")

        cursor = self.mydb.cursor()
        cursor.execute(query)

        product_list = []

        for product in cursor:
            product_name                      = product[0]
            product_description               = product[1]
            quantity_in_wmm_stock             = product[2]
            optimal_stock_quantity            = product[3]
            fill                              = product[4]
            source_quantity                   = product[5]
            source_quantity_unit_fill_minutes = product[6]
            product_unit                      = product[7]
            volume                            = product[8]
            product_volume                    = float(product[9])
            real_id                           = product[10]

            if quantity_in_wmm_stock > (optimal_stock_quantity/4):
                continue

            if source_quantity == 0:
                source_quantity = self.calculate_source_quantity(product_unit, product_volume)

            if source_quantity_unit_fill_minutes == 0:
                source_quantity_unit_fill_minutes = self.calculate_source_quantity_unit_fill_minutes(product_unit, product_volume)
        
            batch        = self.calculate_product_batch(product_unit, product_volume, volume, source_quantity)
            fill_ammount = self.calculate_fill_ammount(fill, batch)
            fill_time    = self.calculate_fill_time(fill_ammount, source_quantity_unit_fill_minutes, batch)

            product_dict = {
            "Name"         : product_name + " " + product_description, 
            "Stock"        : quantity_in_wmm_stock,
            "Optimal"      : optimal_stock_quantity,
            "Fill"         : int(fill_ammount),
            "Fill_Time"    : float(fill_time),   
            "Real_ID"      : real_id,
            "Batch"        : int(batch)     
            }
            product_list.append(product_dict)

        cursor.close()
        return product_list
    
    def calculate_source_quantity(self, product_unit, product_volume):
        if product_unit == "liter":
            if product_volume <= 2.5:
                return 120
            elif product_volume > 2.5:
                return 480
        if product_unit == "kilogram":
            return 25
    
    def calculate_source_quantity_unit_fill_minutes(self, product_unit, product_volume):
        if product_unit == "liter":
            return 60
        if product_unit == "kilogram":
            if product_volume <= 2.5:
                return 30
            elif product_volume > 2.5:
                return 6
            
    def calculate_product_batch(product_unit, product_volume, volume, wsq):
        unit = product_volume if product_unit == "liter" else volume / 1000
        if unit == 0:
            return wsq
        
        if unit > wsq:
            wsq = unit
        return wsq // unit
    
    def calculate_fill_ammount(self, fill, batch):
            if fill < 0: 
                return 0
            p = fill / batch
            if p != int(p):
                return int(p) * batch + batch
            else:
                return p
    
    def calculate_fill_time(self, fill_ammount, source_quantity_unit_fill_minutes, batch):
        return fill_ammount * (source_quantity_unit_fill_minutes / batch)
            

    def dump_fill_time(self, real_id, batch, final_time):
        '''
        Updates the wip_source_quantity_unit_fill_minutes for an individual product

        Parameters:
        real_id (int): The products id
        batch (float): The products batch
        final_time (float): The time of an individual product
        '''
        print("Dumping", real_id, "to the database")
        cursor = self.mydb.cursor()
        query  = ("SELECT real_product_id, `date`, `field`, new_value FROM real_product_changes WHERE `field` = 'wip_source_quantity_unit_fill_mi' AND real_product_id = '"+str(real_id)+"' ORDER BY `date` DESC")
        
        cursor.execute(query)
        new_time = math.ceil(final_time * batch)
        av_time = new_time
        x = 1
        old_time = 0
        for change in cursor:
            if x == 1:
                old_time = change[3]
            x += 1
            if x < 9:
                av_time += int(change[3])
            else:
                break
                	
        if x != 0:
            av_time /= x
        if new_time <= 0:
            return
        query = ("""
            INSERT INTO real_product_changes (real_product_id, `date`, employee_id, `text`, `field`, old_value, new_value)
            VALUES (%s, NOW(), 24, "Veld wip_source_quantity_unit_fill_minutes gewijzigd van %s naar %s.", 'wip_source_quantity_unit_fill_minutes', %s, %s)
             """) 
        

        cursor.execute(query, (str(real_id), str(old_time), str(new_time), str(old_time), str(new_time)))
        self.mydb.commit()

        
        query = ("UPDATE real_products SET wip_source_quantity_unit_fill_minutes = "+str(av_time)+" WHERE real_product_id = "+str(real_id)+";")
        cursor.execute(query)
        self.mydb.commit()
        cursor.close()

        print("Dump Completed")
