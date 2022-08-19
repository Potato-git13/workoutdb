import sqlite3
import sys
import re
from time import strftime
from os.path import exists
from opts import getOpts

options = getOpts(sys.argv[1:])
# Database name
filepath = options.database
# Table names
cat_table_name = "categories"
ent_table_name = "entries"

def msg(message, mode):
    # Modes:
    #   0 - verbose info
    #   1 - error

    if (options.verbose and mode == 0):
        print(f"workoutdb: info: {message}")
    
    if (mode == 1):
        print(f"workoutdb: error: {message}")
        sys.exit()

def db_connect():
    # Check if the file exists
    if (exists(filepath)):
        # Create a connection
        con = sqlite3.connect(filepath)
        msg("database connection established", 0)
    else:
        msg(f"file does not exist {filepath}", 1)
    
    return con

def update_categories(con):
    # Iterate for every category and id
    for cat_id, category in enumerate(con.execute(f"SELECT * FROM {cat_table_name} ORDER BY name")):
        all_count = 0
        try: 
            # Increment the all counter for every entry referencing a category id
            for entry in con.execute(f"SELECT * FROM {ent_table_name} ORDER BY id"):
                if (entry[1] == cat_id):
                    all_count += 1
        except sqlite3.OperationalError:
            pass
        # Update the category table wwith the new counter
        con.execute(f"""UPDATE {cat_table_name}
                        SET all_count = {all_count}
                        WHERE table_id = {cat_id}""")

def init(categories):
    # Create a new database
    try:
        open(filepath, "x")
        msg(f"created file: {filepath}", 0)
    except FileExistsError:
        msg(f"file exists: {filepath}", 0)
    except PermissionError:
        msg(f"do not have permission to create file: {filepath}", 1)
    except Exception as e:
        msg(e, 1)
    
    con = db_connect()

    # Create tables
    try:
        con.execute(f"""CREATE TABLE {cat_table_name}
                    (name text, table_id real, all_count real)""")
        msg(f"created table: {cat_table_name}", 0)
    except sqlite3.OperationalError:
        pass
    try:
        con.execute(f"""CREATE TABLE {ent_table_name}
                    (entry_id real, date text, table_id real)""")
        msg(f"created table: {ent_table_name}", 0)
    except sqlite3.OperationalError:
        pass
    
    # Insert the category data into the categories table
    result = con.execute(f"SELECT COUNT(*) FROM {cat_table_name} LIMIT 1").fetchall()[0][0]
    if (result ==0):
        try:
            for cat_id, category in enumerate(categories):
                all_count = 0
                con.execute(f"INSERT INTO {cat_table_name} VALUES ('{category}', {cat_id}, {all_count})")
                msg(f"inserted values: ({category}, {cat_id}, {all_count}) into table: {cat_table_name}", 0)
        except Exception as e:
            msg(e, 1)
    
    con.commit()
    con.close()
    print("Database initialized!")

def add_entry(category):
    con = db_connect()

    table_id = None
    entry_id = 0
    categories = []
    for entry in con.execute(f"SELECT * FROM {cat_table_name} ORDER BY name"):
        # This will create the full list of categories on loop completion
        categories.append(entry[0])
        # If the entry name and category name match store the table id
        if entry[0] == category:
            table_id = entry[1]
    
    # Count up the entry id
    for entry in con.execute(f"SELECT * FROM {ent_table_name} ORDER BY entry_id"):
        if (entry_id == None):
            entry_id = 0
        entry_id += 1

    # Create an entry
    if (table_id != None):
        con.execute(f"INSERT INTO {ent_table_name} VALUES ({entry_id}, '{strftime('%Y/%m/%d')}', {table_id})")
        print(f"created an entry for category: {category} with date: {strftime('%Y/%m/%d')}")
    else:
        msg(f"category: {category} not recognized", 1)
    
    update_categories(con)
    msg("updated the categories", 0)

    con.commit()
    con.close()

def remove_entry(entry_id):
    con = db_connect()

    try:
        exists = False
        # Check if an entry exists
        for entries in con.execute(f"SELECT * FROM {ent_table_name} WHERE entry_id = {entry_id}"):
            exists = True
            msg(f"found entry with id: {entry_id}", 0)
            break

        if (exists):
            try:
                # Get 1 entry ith given id and delet it
                con.execute(f"DELETE FROM {ent_table_name} WHERE entry_id = {entry_id} LIMIT 1")
            except sqlite3.OperationalError as e:
                msg(e, 1)
            print(f"Deleted newest entry with id: {entry_id} from table: {ent_table_name}")
            
            update_categories(con)
            msg("updated categories", 0)

            con.commit()
            con.close()
        else:
            con.close()
            msg(f"entry with id: {entry_id} does not exist in table: {ent_table_name}", 1)
    except sqlite3.OperationalError as e:
        msg(e, 1)

def read_log(n):
    con = db_connect()
    
    try:
        for entry in con.execute(f"SELECT * FROM {ent_table_name} ORDER BY entry_id DESC LIMIT {n}"):
            for category in con.execute(f"SELECT * FROM {cat_table_name} ORDER BY table_id"):
                if entry[2] == category[1]:
                    print(f"{round(entry[0])}: {entry[1]}: {category[0]}")
    except sqlite3.OperationalError as e:
        msg(e, 1)

def read_entry(args):
    con = db_connect()

    # Get the all value of a category
    if (args[0] == "all"):
        all_value = 0
        category = args[1]
        exists = False
        # Check for category existance
        try:
            for entries in con.execute(f"SELECT * FROM {cat_table_name} WHERE name = '{category}'"):
                exists = True
                msg(f"found category with name: {category}", 0)
                break
        except sqlite3.OperationalError as e:
            con.close()
            msg(e, 1)

        if (exists):
            try: 
                for entry in con.execute(f"SELECT * FROM {cat_table_name} ORDER BY table_id"):
                    # Match the category with one of the entries by name
                    if (entry[0] == category):
                        # Get the all_count from the entry
                        all_value = round(entry[2])
                        break
                print(f"{all_value} entry/ies refrence category: {category}")
                con.close()
            except Error as e:
                con.close()
                msg(e, 1)
        else:
            con.close()
            msg(f"category: {category} does no exist", 1)
    # Get entries for date
    else:
        input_id = int(args[0])

        try:
            for entry in con.execute(f"SELECT * FROM {ent_table_name} ORDER BY entry_id"):
                if (input_id == round(entry[0])):
                    msg("id matched", 0)
                    for category in con.execute(f"SELECT * FROM {cat_table_name} ORDER BY table_id"):
                        if entry[2] == category[1]:
                            msg("category matched", 0)
                            print(f"{round(entry[0])}: {entry[1]}: {category[0]}")
        except sqlite3.OperationalError as e:
            con.close()
            msg(e, 1)

# ---------- MAIN EXECUTION ----------

if (options.init):
    msg("starting: init", 0)
    init(options.init)

if (options.add):
    msg("starting: add_entry", 0)
    add_entry(options.add)

if (options.log):
    msg("starting: read_log", 0)
    n = options.log
    try:
        n = int(n)
        read_log(n)
    except ValueError:
        msg("ENTRIES argument is not a number", 1)

if (options.read):
    msg("starting: read_entry", 0)
    if ((options.read[0].isnumeric() and len(options.read) == 1) or (options.read[0] == "all" and len(options.read) == 2)):
        msg("pattern matched", 0)
        read_entry(options.read)
    else:
        msg("pattern not matched", 1)

if (options.remove):
    msg("starting: remove_entry", 0)
    remove_entry(options.remove)