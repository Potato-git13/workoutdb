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
    if (exists(filepath)):
        con = sqlite3.connect(filepath)
        msg("database connection established", 0)
    else:
        msg(f"file does not exist {filepath}", 1)
    
    return con

def update_categories(con):
    for cat_id, category in enumerate(con.execute(f"SELECT * FROM {cat_table_name} ORDER BY name")):
        all_count = 0
        try: 
            for entry in con.execute(f"SELECT * FROM {ent_table_name} ORDER BY id"):
                if (entry[1] == cat_id):
                    all_count += 1
        except sqlite3.OperationalError:
            pass
        
        con.execute(f"""UPDATE {cat_table_name}
                        SET all_count = {all_count}
                        WHERE id = {cat_id}""")

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
                    (name text, id real, all_count real)""")
        msg(f"created table: {cat_table_name}", 0)
    except sqlite3.OperationalError:
        pass
    try:
        con.execute(f"""CREATE TABLE {ent_table_name}
                    (date text, id real)""")
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

    entry_id = None
    categories = []
    for entry in con.execute(f"SELECT * FROM {cat_table_name} ORDER BY name"):
        categories.append(entry[0])
        if entry[0] == category:
            entry_id = entry[1]
    
    if not (entry_id == None):
        con.execute(f"INSERT INTO {ent_table_name} VALUES ('{strftime('%Y/%m/%d')}', {entry_id})")
        print(f"created an entry for category: {category} with date: {strftime('%Y/%m/%d')}")
    else:
        msg(f"category: {category} not recognized", 1)
    
    update_categories(con)
    msg("updated the categories", 0)

    con.commit()
    con.close()

def remove_entry(date):
    con = db_connect()

    try:
        exists = False
        for entries in con.execute(f"SELECT * FROM {ent_table_name} WHERE date = '{date}'"):
            exists = True
            msg(f"found entry with date: {date}", 0)
            break

        if (exists):
            try:
                con.execute(f"DELETE FROM {ent_table_name} WHERE date = '{date}' ORDER BY id LIMIT 1")
            except sqlite3.OperationalError as e:
                msg(e, 1)
            print(f"Deleted newest entry with date: {date} from table: {ent_table_name}")
            
            update_categories(con)
            msg("updated categories", 0)

            con.commit()
            con.close()
        else:
            con.close()
            msg(f"entry with date: {date} does not exist in table: {ent_table_name}", 1)
    except sqlite3.OperationalError as e:
        msg(e, 1)

def read_log(n):
    con = db_connect()
    
    try:
        for entry in con.execute(f"SELECT * FROM {ent_table_name} ORDER BY date DESC LIMIT {n}"):
            for category in con.execute(f"SELECT * FROM {cat_table_name} ORDER BY id"):
                if entry[1] == category[1]:
                    print(f"{entry[0]}: {category[0]}")
    except sqlite3.OperationalError as e:
        msg(e, 1)

def read_entry(args):
    con = db_connect()

    # Get the all value of a category
    if (args[0] == "all"):
        all_value = 0
        category = args[1]
        exists = False
        try:
            for entries in con.execute(f"SELECT * FROM {cat_table_name} WHERE name = '{category}'"):
                exists = True
                msg(f"found category with name: {category}", 0)
                break
        except sqlite3.OperationalError as e:
            msg(e, 1)

        if (exists):
            try: 
                for entry in con.execute(f"SELECT * FROM {cat_table_name} ORDER BY id"):
                    # Match the category with one of the entries by name
                    if (entry[0] == category):
                        # Get the all_count from the entry
                        all_value = round(entry[2])
                        break
                print(f"{all_value} entry/ies refrence category: {category}")
                con.close()
            except Error as e:
                msg(e, 1)
        else:
            msg(f"category: {category} does no exist", 1)
            con.close()
    # Get entries for date
    else:
        pass

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
    if (re.fullmatch("[0-9]{4}\\/[0-9]{2}\\/[0-9]{2}", options.read[0]) or (options.read[0] == "all" and len(options.read) == 2)):
        msg("pattern matched", 0)
        read_entry(options.read)
    else:
        msg("pattern not matched", 1)

if (options.remove):
    msg("starting: remove_entry", 0)
    if (re.fullmatch("[0-9]{4}\\/[0-9]{2}\\/[0-9]{2}", options.remove)):
        msg("date pattern matched", 0)
        remove_entry(options.remove)
    else:
        msg("date pattern not matched", 1)