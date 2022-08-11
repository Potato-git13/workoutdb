import argparse
import sys

def getOpts(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="workout journal")

    parser.add_argument("database", metavar="DB", help="The database to access")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-i", "--init", nargs="+", metavar="CATEGORIES", help="Initialize a new database. Supply all categories of the db")
    parser.add_argument("-l", "--log", action="store", metavar="ENTRIES", help="Read N amount of entries")
    parser.add_argument("-r", "--read", nargs="+", action="store", metavar="ENTRY", help="Read a specific entry. ENTRY can be a date \"YYYY/MM/DD\" or \"all CATEGORY\"")
    parser.add_argument("-a", "--add", action="store", metavar="CATEGORY", help="Add an entry")
    parser.add_argument("-rm", "--remove", action="store", metavar="DATE", help="Remove newest entry with date DATE")

    options = parser.parse_args(args)
    return options