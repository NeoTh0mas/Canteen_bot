import pymongo
import os
from dotenv import load_dotenv, find_dotenv
import random
from string import ascii_letters
import time

load_dotenv(find_dotenv())
password = os.environ.get("MONGODB_PWD")
signs = ascii_letters + "0123456789"

client = pymongo.MongoClient(f"mongodb+srv://stewart:{password}@database.ead0d.mongodb.net/?retryWrites=true&w=majority&authSource=admin")
db = client.hexagon

profiles = db.profile
tables = db.tables
menu = db.menu
orders = db.orders
vars = db.variables

# create a profile 
def profile_create(surname, name, last_name, group, lang, telegram_id, status=0):
    password= "".join(random.sample(signs, 7))
    document = {
    "telegram_id": telegram_id,
    "surname": surname,
    "name": name,
    "last_name": last_name,
    "group": group,
    "status": status,
    "language": lang,
    "cart": [],
    "cart_deleted": [],
    "password": password
    }

    profiles.insert_one(document)


def profile_update():
    p = profiles.find()
    update = {
        "$set": {"status": 0,}
    }
    for profile in p:
        profiles.update_one({"name": profile["name"], "surname": profile["surname"]}, update)

# profile_update()
# profile_create("Emil", "Emil", "Emil", "1ТН1", "eng", 0)
# print("account was created successfully!")

# check existance of a profile
def profile_check(name, surname, group):
    return profiles.find_one({"name": name, "surname": surname, "group": group})



# read profile info by telegram id 
def profile_find(_id):
    return profiles.find_one({"telegram_id": _id})


# setting a telegram_id for the account that was signed in
def register(_id, name, surname):
    update = {
        "$set": {"telegram_id": _id, "password": ""}
    }
    profiles.update_one({"name": name, "surname": surname}, update)


# checking whether the entered password matches with the actual one
def match_passwords(name, surname, password):
    db_pass = profiles.find_one({"name": name, "surname": surname})["password"]
    return password == db_pass


# change language
def profile_lang_update(_id, lang):
    update = {
        "$set": {"language": lang}
    }
    profiles.update_one({"telegram_id": _id}, update)


# create a table collection
def table_create():
    docs = []
    

    for i in range(1, 25):
        document = {
        "number": i,
        "state": False,
        "name": "",
        "surname": "",
        "group": ""
    }
        docs.append(document)

    tables.insert_many(docs)


# checking if thera are less than 4 tables are reserved by one group
def table_check(group):
    c_time = time.time()
    # return len(list(tables.find({"group": group}))), time.time() - c_time
    # return  len([table["group"] for table in tables.find({"group": group})]), time.time() - c_time
    return tables.count_documents(filter={"group": group}) < 3


# find idle tables with state false
def table_find_idle():
    return [table["number"] for table in tables.find({"state": False})]


# return the information about the reserved tables
def table_find(number):
    return tables.find_one({"number": number})


# setting profile values to reserved table and making the state true
def table_update(number, name, surname, group):
    update = {
        "$set": {"state": True, "name": name, "surname": surname, "group": group}
    }

    tables.update_one({"number": number}, update)


# clear all the values in the tables collection
def table_clean():
    for i in range(1, 25):
        update = {
            "$set": {"state": False, "name": "", "surname": "", "group": ""}
        }
        tables.update_one({"number": i}, update)


# create a menu collection
def menu_create():
    for i in range(1, 23):
        name = input(f"Meal #{i}: ")
        price = int(input("Price: "))
        description = input("Description: ")
        menu.insert_one({"name": name, "price": price, "description": description})


# get all meal names from menu
def menu_get_meal_names():
    return [x["name"] for x in list(menu.find())]


# getting names and prices of the meals
def menu_get():
    return {x["name"]: [x["description"], x["price"]] for x in list(menu.find())}


# adding photo_id field for every meal in the db
def menu_id_add():
    meals = menu_get_meal_names()
    update = {
        "$set": {"photo_id": ""}
    }
    for name in meals:
        print(menu.find_one({"name": name}))
        menu.update_one({"name": name}, update)


# get photo_id
def menu_get_photo(name):
    return menu.find_one({"name": name})["photo_id"]


# user's cart
def cart_create():
    names = [x["name"] for x in profiles.find()]
    update = {
        "$set": {"cart": []}
    }
    for name in names:
        profiles.update_one({"name": name}, update)


# adding one meal to the existing cart of a particular user
def cart_update(id, meal):
    cart = list(profiles.find_one({"telegram_id": id})["cart"])
    cart.append(meal)

    update = {
        "$set": {"cart": cart}
    }
    profiles.update_one({"telegram_id": id}, update)


# get all the meals that have been added to the cart of a particular user
def cart_get(id): 
    cart = profiles.find_one({"telegram_id": id})["cart"]
    
    return cart


# clearing cart as all meals from it were ordered
def cart_clear(id):
    update = {
        "$set": {"cart": []}
    }

    profiles.update_one({"telegram_id": id}, update)


# removing a particular meal from the cart of a user during editing state
def cart_remove(id, meal):
    cart = cart_get(id)
    cart.remove(meal)
    update = {
        "$set": {"cart": cart}
    }

    profiles.update_one({"telegram_id": id}, update)


# get the list of names of deleted meals from the cart
def cart_deleted_list(id):
    return list(profiles.find_one({"telegram_id": id})["cart_deleted"])


# update list of deleted items from the cart
def cart_deleted_update(id, meal):
    deleted = cart_deleted_list(id)
    if deleted == [""]:
        deleted = [f'"{meal}",']
    else:
        deleted.append(f'"{meal}",')
    update = {
        "$set": {"cart_deleted": deleted}
    }
    profiles.update_one({"telegram_id": id}, update)


# reset the deleted list of items after they were printed
def cart_deleted_reset(id):
    update = {
        "$set": {"cart_deleted": []}
    }
    profiles.update_one({"telegram_id": id}, update)


# save an order to the database 
def order_save(id, cart, total, payment, time, name, surname, group):
    order = {
        "telegram_id": id,
        "name": name,
        "surname": surname,
        "group": group,
        "cart": cart,
        "total": total,
        "payment": payment,
        "time": time,
    }

    orders.insert_one(order)


# time period for the order
def time_period():
    update = {
        "$set": {"time_period": False if time_period_get() else True}
    }

    vars.update_one({"time_period": True if time_period_get() else False}, update)


def time_period_get():
    return list(vars.find())[0]["time_period"]
    # return orders.find_one({"_id": "63dd2741a28f8c52e331db69"})["time_period"]


# reset tables and profile info in the database based on schedule
def reset_db():
    profile_reset = {
        "$set": {"cart": []}
    }
    for id in [x["_id"] for x in profiles.find()]:
        profiles.update_one({"_id": id}, profile_reset)


    table_reset = {
        "$set": {"state": False, "name": "", "surname": "", "group": ""}
    }
    for id in [x["_id"] for x in tables.find()]:
        tables.update_one({"_id": id}, table_reset)
    
    print("Database was reset successfully")
