# Filename: database_routines.py
# Python 3.7

import sqlite3 as sql
import csv
import os
import sys

#------------------------------------#
# Create Sqlite3 database and tables #
#------------------------------------#

def create_database():
    """Creates SQLite database and tables, and returns None."""
    if os.path.exists("data_wrangling_project.db"):
        print ("Database already exists...")
        os.remove("data_wrangling_project.db")
        print ("...database deleted")

    try:
        connection = sql.connect("data_wrangling_project.db")
        print ("\nDatabase created...")
    except:
        print ("Error -- cannot connect to the database")
        sys.exit()

    with connection:
        cur = connection.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS nodes (   \
                    id INTEGER PRIMARY KEY NOT NULL,      \
                    lat REAL,                             \
                    lon REAL,                             \
                    user TEXT,                            \
                    uid INTEGER,                          \
                    version INTEGER,                      \
                    changeset INTEGER,                    \
                    timestamp TEXT                        \
                    );")

        cur.execute("CREATE TABLE IF NOT EXISTS nodes_tags (             \
                    id INTEGER NOT NULL,                   \
                    key TEXT,                              \
                    value TEXT,                            \
                    type TEXT,                             \
                    FOREIGN KEY (id) REFERENCES nodes(id)  \
                    );")

        cur.execute("CREATE TABLE IF NOT EXISTS ways (   \
                    id INTEGER PRIMARY KEY NOT NULL,     \
                    user TEXT,                           \
                    uid INTEGER,                         \
                    version TEXT,                        \
                    changeset INTEGER,                   \
                    timestamp TEXT                       \
                    );")

        cur.execute("CREATE TABLE IF NOT EXISTS ways_tags (   \
                    id INTEGER NOT NULL,                      \
                    key TEXT,                                 \
                    value TEXT,                               \
                    type TEXT,                                \
                    FOREIGN KEY (id) REFERENCES ways(id)      \
                    );")

        cur.execute("CREATE TABLE IF NOT EXISTS ways_nodes (      \
                    id INTEGER NOT NULL,                          \
                    node_id INTEGER NOT NULL,                     \
                    position INTEGER NOT NULL,                    \
                    FOREIGN KEY (id) REFERENCES ways(id),         \
                    FOREIGN KEY (node_id) REFERENCES nodes(id)    \
                    );")

    connection.commit()

    cur.close()
    connection.close()
    print ("...database tables created")
    return


#----------------------------------------------------#
# Read CSV files and write data into database tables #
#----------------------------------------------------#

def read_csv_files():
    """Reads CSV files and writes data into database tables, and returns None."""
    if os.path.exists("data_wrangling_project.db"):
        print ("\nDatabase in order...")
    else:
        print ("\nDatabase does not exist...\n")
        sys.exit()

    if not os.path.exists("nodes_tags.csv"):
        print ("Cannot find CSV files...")
        sys.exit()

    try:
        con = sql.connect("data_wrangling_project.db")
        print ("Connected to database...\n")
    except:
        print ("\nError -- cannot connect to the database")
        sys.exit()

    cur = con.cursor()

    nodes_row_count = 0
    nodes_tags_row_count = 0
    ways_row_count = 0
    ways_tags_row_count = 0
    ways_nodes_row_count = 0

    with open('nodes.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)   # comma is default delimiter
        next(csv_file)   # skip header row
        for row in reader:
            cur.execute("INSERT OR ABORT INTO nodes (id, lat, lon, user, uid, version, changeset, timestamp) \
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?);", row)
            nodes_row_count += 1

    print ('Nodes written to db...')
    print ('Nodes number of rows: {:,}'.format(nodes_row_count))
    csv_file.close()

    with open('nodes_tags.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)   # comma is default delimiter
        next(csv_file)   # skip header row
        for row in reader:
            cur.execute("INSERT OR ABORT INTO nodes_tags (id, key, value, type) VALUES (?, ?, ?, ?);", row)
            nodes_tags_row_count += 1

    print ('\nNodes Tags written to db...')
    print ('Nodes Tags number of rows: {:,}'.format(nodes_tags_row_count))
    csv_file.close()

    with open('ways.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)   # comma is default delimiter
        next(csv_file)   # skip header row
        for row in reader:
            cur.execute("INSERT OR ABORT INTO ways (id, user, uid, version, changeset, timestamp) \
                         VALUES (?, ?, ?, ?, ?, ?);", row)
            ways_row_count += 1

    print ('\nWays written to db...')
    print ('Ways number of rows: {:,}'.format(ways_row_count))
    csv_file.close()

    with open('ways_tags.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)   # comma is default delimiter
        next(csv_file)   # skip header row
        for row in reader:
            cur.execute("INSERT OR ABORT INTO ways_tags (id, key, value, type) VALUES (?, ?, ?, ?);", row)
            ways_tags_row_count += 1

    print ('\nWays Tags written to db...')
    print ('Ways Tags number of rows: {:,}'.format(ways_tags_row_count))
    csv_file.close()

    with open('ways_nodes.csv', 'r') as csv_file:
        reader = csv.reader(csv_file)   # comma is default delimiter
        next(csv_file)   # skip header row
        for row in reader:
            cur.execute("INSERT OR ABORT INTO ways_nodes (id, node_id, position) VALUES (?, ?, ?);", row)
            ways_nodes_row_count += 1

    print ('\nWays Nodes written to db...')
    print ('Ways Nodes number of rows: {:,}'.format(ways_nodes_row_count))
    csv_file.close()

    con.commit()
    cur.close()
    con.close()
    return


#----------------------------------------#
# Count the number of rows in each table #
#----------------------------------------#

def count_rows():
    """Counts the number of rows in each database table, prints a report, and returns None."""
    if not os.path.exists("data_wrangling_project.db"):
        print ("\nDatabase does not exist...\n")
        sys.exit()

    try:
        db = sql.connect("data_wrangling_project.db")
    except:
        print ("\nError -- cannot connect to the database")
        sys.exit()

    c = db.cursor()

    query = "select count(*) as num from nodes;"
    c.execute(query)
    rowsn = c.fetchall()

    query = "select count(*) as num from nodes_tags;"
    c.execute(query)
    rowsnt = c.fetchall()

    query = "select count(*) as num from ways;"
    c.execute(query)
    rowsw = c.fetchall()

    query = "select count(*) as num from ways_tags;"
    c.execute(query)
    rowswt = c.fetchall()

    query = "select count(*) as num from ways_nodes;"
    c.execute(query)
    rowswn = c.fetchall()

    print ("\nCount the number of rows in each table:\n")
    print ('Nodes: {:,}'.format(*rowsn[0]))         # * before tuple unpacks the tuple into separate arguments
    print ('Nodes Tags: {:,}'.format(*rowsnt[0]))
    print ('Ways: {:,}'.format(*rowsw[0]))
    print ('Ways Tags: {:,}'.format(*rowswt[0]))
    print('Ways Nodes: {:,}'.format(*rowswn[0]))

    c.close()
    db.close()
    return


#---------------------------------------#
#  Create consolidated database tables  #
#---------------------------------------#

def consolidated_tables():
    """Creates consolidated database tables and returns None."""
    if not os.path.exists("data_wrangling_project.db"):
        print ("\nDatabase does not exist...\n")
        sys.exit()

    try:
        dbConnect = sql.connect("data_wrangling_project.db")
        print ("\nConnected to database...")
    except:
        print ("\nError -- cannot connect to the database")
        sys.exit()

    cur = dbConnect.cursor()

    # Clean up database
    cur.execute("""DROP TABLE IF EXISTS union_all_tags;""")

    cur.execute("""DROP TABLE IF EXISTS nodes_union_ways;""")

    dbConnect.commit()

    # Create a new table to consolidate tag data
    cur.execute("""CREATE TABLE IF NOT EXISTS union_all_tags (  
                id INTEGER NOT NULL,            
                key TEXT,                   
                value TEXT,                 
                type TEXT                
                );""")

    dbConnect.commit()

    cur.execute("""INSERT OR ABORT INTO union_all_tags       
               SELECT id, key, value, type FROM nodes_tags 
               UNION ALL   
               SELECT id, key, value, type FROM ways_tags    
               ;""")

    dbConnect.commit()
    print ("\nConsolidated tag table done...")

    # Create a new table to consolidate user and timestamp data
    cur.execute("""CREATE TABLE IF NOT EXISTS nodes_union_ways (  
                id INTEGER NOT NULL,            
                user TEXT,
                timestamp TEXT,
                lat REAL,
                lon REAL
                );""")

    dbConnect.commit()

    cur.execute("""INSERT OR ABORT INTO nodes_union_ways       
               SELECT id, user, timestamp, lat, lon FROM nodes 
               UNION    
               SELECT id, user, timestamp, NULL as lat, NULL as lon FROM ways    
               ;""")

    dbConnect.commit()
    print ("\nConsolidated user table done\n")

    cur.close()
    dbConnect.close()
    return


#-----------------------------#
#    Table print functions    #
#-----------------------------#

def print_rows_3_cols(rows, title, comment, col1, col2, col3):
    """Prints a table with 3 columns and returns None.
    
    Arguments:
    rows -- the list of rows returned from the SQL query
    title -- the title of the printed table
    comment -- sub-title of the printed table
    col1, col2, col3 -- the names of the columns in the table
    """
    print ("\n" + title + "\n" + "-"*len(title))
    print ("\n" + comment + "\n")
    # Prefix the size requirement with '-' to left justify
    sys.stdout.write("%-30s %-20s %-60s\n" % (col1, col2, col3))
    sys.stdout.write("%-30s %-20s %-60s\n" % ("-"*len(col1), "-"*len(col2), "-"*len(col3)))
    if col3 != '':
        for row in rows:
            sys.stdout.write("%-30s %-20s %-60s\n" % (row[0], row[1], row[2]))
    else:
        for row in rows:
            if row[0] in ['10023', '10024', '10025']:
                sys.stdout.write("%-30s %-20s\n" % (row[0] + ' **', row[1]))
            else:
                sys.stdout.write("%-30s %-20s\n" % (row[0], row[1]))
    return

def print_rows_4_cols(rows, title, col1, col2, col3, col4):
    """Prints a table with 4 columns and returns None.
    
    Arguments:
    rows -- the list of rows returned from the SQL query
    title -- the title of the printed table
    col1, col2, col3, col4 -- the names of the columns in the table
    """
    print ("\n" + title + "\n" + "-"*len(title) + "\n")
    # Prefix the size requirement with '-' to left justify, '+' to right justify
    sys.stdout.write("%-17s %-18s %-56s %-19s\n" % (col1, col2, col3, col4))
    sys.stdout.write("%-17s %-18s %-56s %-19s\n" % ("-"*len(col1), "-"*len(col2), "-"*len(col3), "-"*len(col4)))
    current = rows[0][0]
    for row in rows:
        if row[0] != current:
            print ( )
            
        sys.stdout.write("%-17s %-18s %-56s %-19s\n" % (row[0], row[1], row[2], row[3]))
        current = row[0]
    return

def print_rows_5_cols(rows, title, col1, col2, col3, col4, col5):
    """Prints a table with 5 columns and returns None.
    
    Arguments:
    rows -- the list of rows returned from the SQL query
    title -- the title of the printed table
    col1, col2, col3, col4, col5 -- the names of the columns in the table
    """
    print ("\n" + title + "\n" + "-"*len(title) + "\n")
    # Prefix the size requirement with '-' to left justify, '+' to right justify
    sys.stdout.write("%-12s %-17s %-59s %-13s %-13s\n" % (col1, col2, col3, col4, col5))
    sys.stdout.write("%-12s %-17s %-59s %-13s %-13s\n" % ("-"*len(col1), "-"*len(col2), "-"*len(col3), 
                                                          "-"*len(col4), "-"*len(col5)))
    current = rows[0][0]
    for row in rows:
        if len(row[2]) > 55:
            n = 58
            s = [ ]
            for i in range(0, len(row[2]), n):
                s.append(row[2][i:i+n])

            print ( )
            for p in s:
                sys.stdout.write("%-12s %-17s %-59s %-13s %-13s\n" % (row[0], row[1], p, row[3], row[4]))
                current = row[0]
                
            continue
        
        if row[0] != current:
            print ( )
        
        sys.stdout.write("%-12s %-17s %-59s %-13s %-13s\n" % (row[0], row[1], row[2], row[3], row[4]))
        current = row[0]
    return

#------------------------#
#  SQL database queries  #
#------------------------#

def queries():
    """Executes SQL database queries, prints tables of results, and returns None."""
    if not os.path.exists("data_wrangling_project.db"):
        print ("\nDatabase does not exist...\n")
        sys.exit()

    try:
        db = sql.connect("data_wrangling_project.db")
    except:
        print ("\nError -- cannot connect to the database")
        sys.exit()

    c = db.cursor()

    title = 'Dates of data entry'
    comment = '  Provides the Age of the Data \n  Oldest date first, in descending order'
    col1 = 'Timestamp'
    col2 = 'Count'
    col3 = 'Username'
    query = "SELECT timestamp, COUNT(timestamp), user FROM nodes_union_ways   \
             GROUP BY timestamp ORDER BY timestamp ASC LIMIT 10;"
    c.execute(query)
    rows = c.fetchall()
    if rows == []:
        print ("\n" + title)
        print ("...Warning: No data found!!")
    else:
        print_rows_3_cols(rows, title, comment, col1, col2, col3)

    title = 'Zip code'
    comment = '  List of the Zip Codes \n  ** indicates Upper West Side'
    col1 = 'Zip code'
    col2 = 'Count'
    col3 = ''
    query = "SELECT value, COUNT(value) as Number FROM union_all_tags   \
             WHERE key = 'postcode'                                     \
             GROUP BY value ORDER BY Number DESC LIMIT 10;"
    c.execute(query)
    rows = c.fetchall()
    if rows == []:
        print ("\n" + title)
        print ("...Warning: No data found!!")
    else:
        print_rows_3_cols(rows, title, comment, col1, col2, col3)

    title = 'Burger Joints on the Upper West Side'
    col1 = 'ID'
    col2 = 'Key'
    col3 = 'Value'
    col4 = 'Timestamp'
    query = "SELECT union_all_tags.id, key, value, timestamp FROM union_all_tags                            \
             INNER JOIN nodes_union_ways                                                                    \
             ON nodes_union_ways.id = union_all_tags.id                                                     \
             WHERE union_all_tags.id IN (SELECT id FROM union_all_tags                                      \
                                         WHERE key = 'cuisine' AND value = 'Burger'                         \
                                         INTERSECT                                                          \
                                         SELECT id FROM union_all_tags                                      \
                                         WHERE key = 'postcode' AND value IN ('10023', '10024', '10025')    \
                                         )                                                                  \
             ;"
    c.execute(query)
    rows = c.fetchall()
    if rows == []:
        print ("\n" + title)
        print ("...Warning: No data found!!")
    else:
        print_rows_4_cols(rows, title, col1, col2, col3, col4)

    title = "Bookshops on the Upper West Side"
    col1 = 'ID'
    col2 = 'Key'
    col3 = 'Value'
    col4 = 'Timestamp'
    query = "SELECT union_all_tags.id, key, value, timestamp FROM union_all_tags                            \
             INNER JOIN nodes_union_ways                                                                    \
             ON nodes_union_ways.id = union_all_tags.id                                                     \
             WHERE union_all_tags.id IN (SELECT id FROM union_all_tags                                      \
                                         WHERE key = 'shop' AND value = 'books'                         \
                                         INTERSECT                                                          \
                                         SELECT id FROM union_all_tags                                      \
                                         WHERE key = 'postcode' AND value IN ('10023', '10024', '10025')    \
                                         )                                                                  \
             ;"
    c.execute(query)
    rows = c.fetchall()
    if rows == []:
        print ("\n" + title)
        print ("...Warning: No data found!!")
    else:
        print_rows_4_cols(rows, title, col1, col2, col3, col4)

    title = 'RadioShack'
    col1 = 'ID'
    col2 = 'Key'
    col3 = 'Value'
    col4 = 'Timestamp'
    query = "SELECT union_all_tags.id, key, value, timestamp FROM union_all_tags   \
             INNER JOIN nodes_union_ways    \
             ON nodes_union_ways.id = union_all_tags.id    \
             WHERE union_all_tags.id IN (SELECT id FROM union_all_tags   \
                                         WHERE key = 'name' AND value IN ('RadioShack', 'Radio Shack', 'Radioshack')  \
                                         INTERSECT    \
                                         SELECT id FROM union_all_tags   \
                                         WHERE key = 'postcode' AND value IN ('10023', '10024', '10025')    \
                                         )    \
             ;"
    c.execute(query)
    rows = c.fetchall()
    if rows == []:
        print ("\n" + title)
        print ("...Warning: No data found!!")
    else:
        print_rows_4_cols(rows, title, col1, col2, col3, col4)



    title = 'Inscription'
    col1 = 'ID'
    col2 = 'Key'
    col3 = 'Value'
    col4 = 'Latitude'
    col5 = 'Longitude'
    query = "SELECT union_all_tags.id, key, value,           \
               CASE WHEN lat IS NOT NULL                     \
               THEN lat                                      \
               ELSE ' '                                      \
               END,                                          \
               CASE WHEN lon IS NOT NULL                     \
               THEN lon                                      \
               ELSE ' '                                      \
               END                                           \
             FROM union_all_tags                             \
             INNER JOIN nodes_union_ways                     \
             ON nodes_union_ways.id = union_all_tags.id      \
             WHERE union_all_tags.id IN (SELECT id FROM union_all_tags                                         \
                                         WHERE key IN ('inscription_1', 'inscription_2', 'inscription_date',   \
                                                       'nrhp:inscription_date')                                \
                                         )                 \
             ;"
    c.execute(query)
    rows = c.fetchall()
    if rows:
        print_rows_5_cols(rows, title, col1, col2, col3, col4, col5)
    else:
        print ('\nQuery: No data retrieved from database!\n')

    c.close()
    db.close()
    return


def run_database_routines():
    """Creates an Sqlite3 db, loads the data, counts the rows, executes SQL queries, and returns None."""
    if not os.path.exists("nodes_tags.csv"):
        print ("Cannot find CSV files...")
        sys.exit()

    create_database()
    read_csv_files()
    count_rows()
    consolidated_tables()
    queries()
    return

#========================#
#         Runner         #
#========================#

if __name__ == '__main__':
    run_database_routines()
