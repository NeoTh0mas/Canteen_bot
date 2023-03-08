import pymongo
import os
from dotenv import load_dotenv, find_dotenv
import random
from string import ascii_letters
import time
from datetime import datetime, timedelta

# load_dotenv(find_dotenv())
password = os.environ.get("MONGODB_PWD")
signs = ascii_letters + "0123456789"

client = pymongo.MongoClient(f"mongodb+srv://stewart:{password}@database.ead0d.mongodb.net/?retryWrites=true&w=majority&authSource=admin")
db = client.hexagon

profiles = db.profile
tables = db.tables
p1 = db.period1
p2 = db.period2
p3 = db.period3
menu = db.menu
orders = db.orders
vars = db.variables
bugs = db.bug_reports

# create a profile 
def profile_create(surname, name, last_name, group, lang, telegram_id):
    password= "".join(random.sample(signs, 7))
    document = {
    "telegram_id": telegram_id,
    "surname": surname,
    "name": name,
    "last_name": last_name,
    "group": group,
    "language": lang,
    "password": password
    }

    profiles.insert_one(document)


def profile_update():
    p = profiles.find()
    update = {
        "$set": {"period": 0,}
    }
    for profile in p:
        profiles.update_one({"name": profile["name"], "surname": profile["surname"]}, update)

# profile_update()
# profile_create("Альяна", "Альяна", "Альяна", "2ТН2", "ru", 0)
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
        "$set": {"telegram_id": _id, "status": 0, "cart": [], "cart_deleted": [], "table": 0, "time_of_joining": (datetime.now() - timedelta(minutes=30)).strftime("%d.%m.%Y %H:%M:%S")},
        "$unset": {"password": ""}
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
        "reserver": [],
        "seats": 4,
    }
        docs.append(document)

    tables.insert_many(docs)


# checking if there are less than 4 tables reserved by one group
def table_check(group):
    c_time = time.time()
    # return len(list(tables.find({"group": group}))), time.time() - c_time
    # return  len([table["group"] for table in tables.find({"group": group})]), time.time() - c_time
    return tables.count_documents(filter={"group": group}) < 3


def table_check_profile(_id):
    return True if profiles.find_one({"telegram_id": _id})["table"] else False


# find idle tables with state false
def table_find_idle(period):
    if period == 1:
        return sorted([table["number"] for table in p1.find({"state": False})])
    elif period == 2:
        return sorted([table["number"] for table in p2.find({"state": False})])
    elif period == 3:
        return sorted([table["number"] for table in p3.find({"state": False})])


# return the information about the reserved tables
def table_find(number, period):
    if period == 1:
        return p1.find_one({"number": number})
    elif period == 2:
        return p2.find_one({"number": number})
    elif period == 3:
        return p3.find_one({"number": number})


# get number of seats and seats of the needed table
def get_seats(number, period):
    if period == 1:
        table = p1.find_one({"number": number})
        return table["num_of_seats"], table["seats"] 
    elif period == 2:
        table = p2.find_one({"number": number})
        return table["num_of_seats"], table["seats"]
    elif period == 3:
        table = p3.find_one({"number": number})
        return table["num_of_seats"], table["seats"]


def people_find(group):
    people = profiles.find({"group": group, "table": 0})
    return [f'{person["name"]} {person["surname"]}' for person in people]


def add_person(name, surname, number, period):
    update = {
        "$set": {"table": number, "period": period}
    }
    
    seat_update = {
        "$set": {"seats": list(get_seats(number, period)[1]) + [f'{name} {surname}']}
    }

    if period == 1:
        p1.update_one({"number": number}, seat_update)
    elif period == 2:
        p2.update_one({"number": number}, seat_update)
    elif period == 3:
        p3.update_one({"number": number}, seat_update)
    profiles.update_one({"name": name, "surname": surname}, update)


def remove_person(name, surname, number, period):
    people = list(get_seats(number, period)[1])
    people.remove(f'{name} {surname}')
    update = {
        "$set": {"table": 0, "period": 0}
    }
    seat_update = {
        "$set": {"seats": people}
    }

    if period == 1:
        p1.update_one({"number": number}, seat_update)
    elif period == 2:
        p2.update_one({"number": number}, seat_update)
    elif period == 3:
        p3.update_one({"number": number}, seat_update)
    profiles.update_one({"name": name, "surname": surname}, update)

# setting profile values to reserved table and making the state true
def table_update(number, name, surname, group, period):
    update = {
        "$set": {"state": True, "reserver": [name, surname, group]}
    }

    if period == 1:
        p1.update_one({"number": number}, update)
    elif period == 2:
        p2.update_one({"number": number}, update)
    elif period == 3:
        p3.update_one({"number": number}, update)
    

    update_profile = {"$set": {"table": number, "period": period}}
    profiles.update_one({"name": name, "surname": surname, "group": group}, update_profile)

# clear all the values in the tables collection
def table_clean():
    for i in range(1, 25):
        update = {
            "$set": {"state": False, "name": "", "surname": "", "group": ""}
        }
        tables.update_one({"number": i}, update)
    

def table_reset(table, period):
    table = table_find(table, period)
    table_update = {
        "$set": {"state": False, "reserver": [], "seats": []}
    }
    seats_update = {
        "$set": {"table": 0, "period": 0}
    }

    if table['seats']:
        for person in table["seats"]:
            name, surname = person.split()
            profiles.update_one({"name": name, "surname": surname}, seats_update)

    if table['reserver']:
        profiles.update_one({"name": table["reserver"][0], "surname": table["reserver"][1]}, seats_update)


    if period == 1:
        p1.update_one({"number": table['number']}, table_update)
    elif period == 2:
        p2.update_one({"number": table['number']}, table_update)
    elif period == 3:
        p3.update_one({"number": table['number']}, table_update)


# temp
def table_edit():
    table_reset = {
        "$set": {"state": False, "seats": 0, "reserver": []}
    }
    for id in [x["_id"] for x in tables.find()]:
        tables.update_one({"_id": id}, table_reset)


# temp
def seats_update():
    for i in range(1, 25):
        table = table_find(i)["seats"]
        update = {
            "$set": {"seats": []}
        }
        for j in [p1, p2, p3]:
            j.update_one({"number": i}, update)


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
def order_save(id, cart, total, payment, name, surname, group):
    order = {
        "telegram_id": id,
        "name": name,
        "surname": surname,
        "group": group,
        "cart": cart,
        "total": total,
        "payment": payment,
        "time": (datetime.now() - timedelta(minutes=30)).strftime("%d.%m.%Y %H:%M:%S")
    }

    orders.insert_one(order)


def bug_save(telegram_id, user, description, photo_id):
    profile = profile_find(telegram_id)
    bug = {
        "name": profile["name"],
        "surname": profile["surname"],
        "group": profile["group"],
        "telegram_user": f"@{user}",
        "description": description,
        "photo_id": photo_id,
        "date": (datetime.now() - timedelta(minutes=30)).strftime("%d.%m.%Y %H:%M:%S")
    }

    bugs.insert_one(bug)


# time period for the order
def time_period():
    update = {
        "$set": {"time_period": False if time_period_get() else True}
    }

    vars.update_one({"time_period": True if time_period_get() else False}, update)


def time_period_get():
    return list(vars.find())[0]["time_period"]


# reset tables and profile info in the database based on schedule
def reset_db():
    profile_reset = {
        "$set": {"cart": [], "table": 0, "period": 0}
    }
    for id in [x["_id"] for x in profiles.find()]:
        profiles.update_one({"_id": id}, profile_reset)
    
    for period in range(1, 4):
        for table in range(1, len(list(p1.find())) + 1):
            table_reset(table, period)
    
    print("Database was reset successfully")
