# Filename: database_age_plot.py
# Python 3.7

import sqlite3 as sql
import matplotlib.pyplot as plt
from datetime import datetime
from operator import itemgetter
import sys
import os

def print_rows_2Columns(title, rows):
    """Prints a table with 2 columns and returns None.
    
    Arguments:
    title -- the title of the printed table
    rows -- the list of rows returned from the SQL query
    """
    print ('')
    print (title.ljust(24), "\t Count")
    print (("-------").ljust(24), "\t -----\n")
    for row in rows:
        print (str(row[0]).ljust(24), "\t", row[1])    
    return

#======================#
#     Main routine     #
#======================#

# Plot the distribution of the age of the data

def plot_dates():
    """Plots the distribution of the age of the data, and returns None."""
    if not os.path.exists("data_wrangling_project.db"):
        print ("\nDatabase does not exist...\n")
        sys.exit()

    try:
        db = sql.connect("data_wrangling_project.db")
    except:
        print ("\nError -- cannot connect to the database")
        sys.exit()

    c = db.cursor()

    title = 'Timestamp'
    query = "SELECT timestamp, count(timestamp) FROM nodes_union_ways GROUP BY timestamp ORDER BY timestamp;"

    c.execute(query)
    rows = c.fetchall()
    # print_rows_2Columns(title, rows)
    # print ('\n---------------------------------------')

    c.close()
    db.close()

    x = [ ]
    y =[ ]
    ticks = [ ]
    tocks = [ ]
    date_format = "%Y-%m-%dT%H:%M:%SZ"

    for t in range(2007,2020,1):
        ticks.append(datetime.strptime(str(t), "%Y"))

    for t in range(0, 110, 10):
        tocks.append(t)

    for row in rows:
        try:
            datetime_object = datetime.strptime(row[0], date_format)
        except:
            print ('String to date time conversion error!!')

        x.append(datetime_object)
        y.append(row[1])

    print ()
    plt.figure(figsize=(11,7), clear = True)
    ax = plt.subplot(111)
    ax.bar(x, y, width = 200, color = (179/255.0, 204/255.0, 1.0))      # RGB color [0, 1.0] float divide by 255
    ax.xaxis_date()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    plt.xticks(ticks)
    plt.yticks(tocks)
    plt.xlabel('Date')
    plt.ylabel('Date Counts')
    plt.title('Distribution of Date Range\n')

    plt.show()

    sort_list = sorted(rows, key=itemgetter(0))
    length = len(sort_list)
    median_index = (length - 1) // 2      # integer division (quotient without remainder)

    print (' '*5 + 'Number of dates: {:,}'.format(length) )
    print (' '*5 + 'Date range: ')
    oldest = sort_list[0][0]              # minimum
    newest = sort_list[length - 1][0]     # maximum
    print (' '*5 + oldest[:10] + '  to  ' + newest[:10])
    print (' '*5 + 'Median date:', sort_list[median_index][0][:10])

    rows.clear()
    return

if __name__ == "__main__":
    plot_dates()
