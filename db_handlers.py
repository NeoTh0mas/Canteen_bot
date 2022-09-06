import pymongo
import os
from dotenv import load_dotenv, find_dotenv
from bson.objectid import ObjectId

load_dotenv(find_dotenv())
password = os.environ.get("MONGODB_PWD")

client = pymongo.MongoClient(f"mongodb+srv://stewart:{password}@database.ead0d.mongodb.net/?retryWrites=true&w=majority&authSource=admin")
db = client.hexagon

profiles = db.profile
tables = db.tables
menu = db.menu


# create a profile 
def profile_create(name, surname, group, lang, telegram_id):
    document = {
    "name": name,
    "surname": surname,
    "group": group,
    "lang": lang,
    "telegram_id": telegram_id
    }

    profiles.insert_one(document)


# read profile info by telegram id 
def profile_find(_id):  
    return profiles.find_one({"telegram_id": _id})


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


# reset tables and profile info in the database based on schedule
def reset_db():
    profile_reset = {
        "$set": {"cart": []}
    }
    profiles.update_many([user for user in profiles.find()], profile_reset)


    table_reset = {
        "$set": {"state": False, "name": "", "surname": "", "group": ""}
    }
    tables.update_many([table for table in tables.find()], table_reset)
