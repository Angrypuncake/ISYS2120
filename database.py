#!/usr/bin/env python3
# Imports
import pg8000
import configparser
import sys
import bcrypt

#  Common Functions
##     database_connect()
##     dictfetchall(cursor,sqltext,params)
##     dictfetchone(cursor,sqltext,params)
##     print_sql_string(inputstring, params)


################################################################################
# Connect to the database
#   - This function reads the config file and tries to connect
#   - This is the main "connection" function used to set up our connection
################################################################################

def database_connect():
    # Read the config file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Connection target and fallback
    connection_target = 'DATABASE'
    
    # Try to retrieve the necessary configuration from the file
    try:
        # Extract connection parameters from config file
        database = config[connection_target].get('database', config[connection_target]['user'])
        user = config[connection_target]['user']
        password = config[connection_target]['password']
        host = config[connection_target]['host']
        port = int(config[connection_target]['port'])

    except KeyError as e:
        logging.error(f"Missing required config parameter: {e}")
        return None
    
    connection = None

    try:
        # Establish the connection
        connection = pg8000.connect(database=database, user=user, password=password, host=host, port=port)
        
        # Set the schema
        with connection.cursor() as cursor:
            cursor.execute("SET SCHEMA 'airline';")

    except pg8000.OperationalError as e:
        logging.error("Operational error while connecting to the database: Check your credentials or network.")
        logging.error(e)
    except pg8000.ProgrammingError as e:
        logging.error("Programming error in database connection or schema setup: Please check the configuration.")
        logging.error(e)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        return connection

######################################
# Database Helper Functions
######################################
def dictfetchall(cursor,sqltext,params=[]):
    """ Returns query results as list of dictionaries."""
    """ Useful for read queries that return 1 or more rows"""

    result = []
    
    cursor.execute(sqltext,params)
    if cursor.description is not None:
        cols = [a[0] for a in cursor.description]
        
        returnres = cursor.fetchall()
        if returnres is not None or len(returnres > 0):
            for row in returnres:
                result.append({a:b for a,b in zip(cols, row)})

    # print("returning result: ",result)
    return result

def dictfetchone(cursor,sqltext,params=None):
    """ Returns query results as list of dictionaries."""
    """ Useful for create, update and delete queries that only need to return one row"""

    result = []
    cursor.execute(sqltext,params)
    if (cursor.description is not None):
        # print("cursor description", cursor.description)
        cols = [a[0] for a in cursor.description]
        returnres = cursor.fetchone()
        # print("returnres: ", returnres)
        if (returnres is not None):
            result.append({a:b for a,b in zip(cols, returnres)})
    return result


#####################################
##  Update Single Items by PK       #
#####################################


# Update a single user
def update_single_user(userid, firstname, lastname, userroleid, password):
    conn = database_connect()
    if conn is None:
        return None

    cur = conn.cursor()

    try:
        setitems = []
        values = []

        if firstname is not None:
            setitems.append("firstname = %s")
            values.append(firstname)
        if lastname is not None:
            setitems.append("lastname = %s")
            values.append(lastname)
        if userroleid is not None:
            setitems.append("userroleid = %s::bigint")
            values.append(userroleid)
        if password is not None:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            setitems.append("password = %s")
            values.append(hashed_password)

        if setitems:
            sql = f"UPDATE users SET {', '.join(setitems)} WHERE userid = %s;"
            values.append(userid)
            print_sql_string(sql, tuple(values))
            cur.execute(sql, tuple(values))
            conn.commit()
    except Exception as e:
        conn.rollback()  # Rollback if there's an error
        print(f"Error updating user: {e}")
        raise
    finally:
        cur.close()
        conn.close()



##  Insert / Add



def add_user_insert(userid, firstname, lastname, userroleid, password):
    conn = database_connect()
    if conn is None:
        return None
    cur = conn.cursor()

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    sql = """
        INSERT into Users(userid, firstname, lastname, userroleid, password)
        VALUES (%s, %s, %s, %s, %s);
    """
    print_sql_string(sql, (userid, firstname, lastname, userroleid, hashed_password))
    try:
        cur.execute(sql, (userid, firstname, lastname, userroleid, hashed_password))
        conn.commit()  # Commit the transaction
    except Exception as e:
        conn.rollback()  # Rollback if there's an error
        print(f"Unexpected error adding a user: {e}")
        raise
    finally:
        cur.close()
        conn.close()



##################################################
# Print a SQL string to see how it would insert  #
##################################################

def print_sql_string(inputstring, params=None):
    """
    Prints out a string as a SQL string parameterized assuming all strings
    """
    if params is not None:
        if params != []:
           inputstring = inputstring.replace("%s","'%s'")
    
    print(inputstring % params)


###############
# Login       #
###############

def check_login(username, password):
    '''
    Check Login given a username and password
    '''
    # Ask for the database connection, and get the cursor set up
    conn = database_connect()
    print("checking login")


    if conn is None:
        return None
    cur = conn.cursor()


    try:
        sql = """SELECT *
                FROM Users
                    JOIN UserRoles ON
                        (Users.userroleid = UserRoles.userroleid)
                WHERE userid = %s"""
        print_sql_string(sql, (username,))
       
        result = dictfetchone(cur, sql, (username,))  # Fetch the first row
       
        if result:
            user_data = result[0]  # Get the first (and only) dictionary from the list
            stored_password = user_data['password']  # Access password using key
           
            # Check if the entered password matches the stored hashed password
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                return result  
            else:
                print("Invalid password")
                return None
        else:
            print("User not found")
            return None


    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Error Invalid Login")
    finally:
        cur.close()                    
        conn.close()                    
   
    return None

    
########################
#List All Items#
########################

# Get all the rows of users and return them as a dict
def list_users():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        # If a connection cannot be established, send an Null object
        return None
    # Set up the rows as a dictionary
    cur = conn.cursor()
    returndict = None

    try:
        # Set-up our SQL query
        sql = """SELECT *
                    FROM users """
        
        # Retrieve all the information we need from the query
        returndict = dictfetchall(cur,sql)

        # report to the console what we recieved
        print(returndict)
    except:
        # If there are any errors, we print something nice and return a null value
        import traceback
        traceback.print_exc()
        print("Error Fetching from Database", sys.exc_info()[0])

    # Close our connections to prevent saturation
    cur.close()
    conn.close()

    # return our struct
    return returndict
    

def list_userroles():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        # If a connection cannot be established, send an Null object
        return None
    # Set up the rows as a dictionary
    cur = conn.cursor()
    returndict = None

    try:
        # Set-up our SQL query
        sql = """SELECT *
                    FROM userroles """
        
        # Retrieve all the information we need from the query
        returndict = dictfetchall(cur,sql)

        # report to the console what we recieved
        print(returndict)
    except:
        # If there are any errors, we print something nice and return a null value
        print("Error Fetching from Database", sys.exc_info()[0])

    # Close our connections to prevent saturation
    cur.close()
    conn.close()

    # return our struct
    return returndict
    

########################
#List Single Items#
########################

# Get all rows in users where a particular attribute matches a value
def list_users_equifilter(attributename, filterval):
    # Get the database connection and set up the cursor
    conn = database_connect()
    if conn is None:
        return None

    # Allowed attributes to filter by
    allowed_attributes = ['userid', 'username', 'email', 'userroleid']  # Update this list based on your schema

    # Validate the attribute name
    if attributename not in allowed_attributes:
        print(f"Invalid attribute name: {attributename}")
        return None

    # Set up the rows as a dictionary
    cur = conn.cursor()
    val = None

    try:
        # Prepare the SQL statement using a placeholder
        sql = f"""SELECT *
                   FROM users
                   WHERE {attributename} = %s """
        
        # Execute the query safely
        val = dictfetchall(cur, sql, (filterval,))
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error Fetching from Database: {e}")
    finally:
        cur.close()  # Ensure the cursor is closed
        conn.close()  # Ensure the connection is closed

    return val

    


########################### 
#List Report Items #
###########################
    
# # A report with the details of Users, Userroles
def list_consolidated_users():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        # If a connection cannot be established, send an Null object
        return None
    # Set up the rows as a dictionary
    cur = conn.cursor()
    returndict = None

    try:
        # Set-up our SQL query
        sql = """SELECT *
                FROM users 
                    JOIN userroles 
                    ON (users.userroleid = userroles.userroleid) ;"""
        
        # Retrieve all the information we need from the query
        returndict = dictfetchall(cur,sql)

        # report to the console what we recieved
        print(returndict)
    except:
        # If there are any errors, we print something nice and return a null value
        print("Error Fetching from Database", sys.exc_info()[0])

    # Close our connections to prevent saturation
    cur.close()
    conn.close()

    # return our struct
    return returndict

def list_user_stats():
    # Get the database connection and set up the cursor
    conn = database_connect()
    if(conn is None):
        # If a connection cannot be established, send an Null object
        return None
    # Set up the rows as a dictionary
    cur = conn.cursor()
    returndict = None

    try:
        # Set-up our SQL query
        sql = """SELECT userroleid, COUNT(*) as count
                FROM users 
                    GROUP BY userroleid
                    ORDER BY userroleid ASC ;"""
        
        # Retrieve all the information we need from the query
        returndict = dictfetchall(cur,sql)

        # report to the console what we recieved
        print(returndict)
    except:
        # If there are any errors, we print something nice and return a null value
        print("Error Fetching from Database", sys.exc_info()[0])

    # Close our connections to prevent saturation
    cur.close()
    conn.close()

    # return our struct
    return returndict
    

####################################
##  Search Items - inexact matches #
####################################

# Search for users with a custom filter
# filtertype can be: '=', '<', '>', '<>', '~', 'LIKE'
def search_users_customfilter(attributename, filtertype, filterval):
    # Get the database connection and set up the cursor
    conn = database_connect()
    if conn is None:
        return None

    # Allowed attributes and operators to filter by
    allowed_attributes = ['userid', 'username', 'email', 'userroleid','firstname','lastname']  # Allowed attributes
    allowed_filter_types = ['=', '<', '>', '<>', 'LIKE', '~']  # Allowed operators

    # Validate the attribute name
    if attributename not in allowed_attributes:
        print(f"Invalid attribute name: {attributename}")
        return None

    # Validate the filter type
    if filtertype not in allowed_filter_types:
        print(f"Invalid filter type: {filtertype}")
        return None

    cur = conn.cursor()
    val = None

    # Prepare the LIKE filter if applicable
    filtervalprefix = ""
    filtervalsuffix = ""
    if str.lower(filtertype) == "like":
        filtervalprefix = "'%"
        filtervalsuffix = "%'"

    try:
        # Prepare the SQL statement
        sql = f"""SELECT *
                   FROM users
                   WHERE lower({attributename}) {filtertype} {filtervalprefix}lower(%s){filtervalsuffix} """
        
        # Execute the query safely
        val = dictfetchall(cur, sql, (filterval,))
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error Fetching from Database: {e}")
    finally:
        cur.close()  # Ensure the cursor is closed
        conn.close()  # Ensure the connection is closed

    return val


##  Delete
###     delete_user(userid)
def delete_user(userid):
    conn = database_connect()
    if conn is None:
        return None

    cur = conn.cursor()
    try:
        sql = "DELETE FROM users WHERE userid = %s;"
        cur.execute(sql, (userid,))
        conn.commit()  # Commit the transaction
    except Exception as e:
        conn.rollback()  # Rollback if there's an error
        print(f"Unexpected error deleting user with id {userid}: {e}")
        raise
    finally:
        cur.close()
        conn.close()




# 1. List All Aircrafts
def list_aircraft():
    conn = database_connect()
    if conn is None:
        return None
    cursor = conn.cursor()
    try:
        # Set-up our SQL query
        query = "SELECT * FROM aircraft ORDER BY aircraftid ASC"
        # Use dictfetchall to fetch the result as dictionaries
        aircrafts = dictfetchall(cursor, query)
        return aircrafts
    except Exception as e:
        print(f"Unexpected error listing aircraft: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

# 2. Get Aircraft by ID
def get_aircraft_by_id(aircraft_id):
    conn = database_connect()
    if conn is None:
        return None
    cursor = conn.cursor()
    try:
        # SQL query to get a single aircraft by ID
        query = "SELECT * FROM aircraft WHERE aircraftid = %s"
        # Use dictfetchone to fetch the result as a dictionary
        aircraft = dictfetchone(cursor, query, [aircraft_id])
        # dictfetchone returns a list, so return the first element if found
        return aircraft[0] if aircraft else None
    except Exception as e:
        print(f"Unexpected error getting aircraft by ID: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

# 3. Add New Aircraft (No changes needed here, this is for inserting data)
def add_aircraft(aircraft_id, icao_code, registration, manufacturer, model, capacity):
    conn = database_connect()
    if conn is None:
        return None
    cursor = conn.cursor()
    try:
        query = """
        INSERT INTO aircraft (aircraftid, icaocode, aircraftregistration, manufacturer, model, capacity)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (aircraft_id, icao_code, registration, manufacturer, model, capacity))
        conn.commit()  # Commit the transaction
    except Exception as e:
        conn.rollback()  # Rollback if there's an error
        print(f"Unexpected error adding aircraft: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# 4. Update Aircraft (No changes needed here, this is for updating data)
def update_aircraft(aircraft_id, icao_code, registration, manufacturer, model, capacity):
    conn = database_connect()
    if conn is None:
        return None
    cursor = conn.cursor()
    try:
        query = """
        UPDATE aircraft
        SET icaocode = %s, aircraftregistration = %s, manufacturer = %s, model = %s, capacity = %s
        WHERE aircraftid = %s
        """
        cursor.execute(query, (icao_code, registration, manufacturer, model, capacity, aircraft_id))
        conn.commit()
    except Exception as e:
        print(f"Unexpected error updating aircraft: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

# 5. Delete Aircraft (No changes needed here, this is for deleting data)
def delete_aircraft(aircraft_id):
    conn = database_connect()
    if conn is None:
        return None
    cursor = conn.cursor()
    try:
        query = "DELETE FROM aircraft WHERE aircraftid = %s"
        cursor.execute(query, (aircraft_id,))
        conn.commit()
    except Exception as e:
        print(f"Unexpected error deleting aircraft: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

# 6. Aircraft Summary (example: grouped by manufacturer)
def aircraft_summary():
    conn = database_connect()
    if conn is None:
        return None
    cursor = conn.cursor()
    try:
        query = """
        SELECT manufacturer, COUNT(*) AS total_aircraft
        FROM aircraft
        GROUP BY manufacturer
        """
        summary = dictfetchall(cursor, query)
        return summary
    except Exception as e:
        print(f"Unexpected error getting aircraft summary: {e}")
        return None
    finally:
        cursor.close()
        conn.close()