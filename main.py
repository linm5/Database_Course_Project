import pandas as pd
import psycopg2
from psycopg2 import Error
from sqlalchemy import create_engine, text
from pathlib import Path
import matplotlib.pyplot as plt

def run_sql_from_file(sql_file, psql_conn):
    """
    read a SQL file with multiple stmts and process it
    adapted from an idea by JF Santos
    Note: not really needed when using dataframes.
    """
    sql_command = ""
    for line in sql_file:
        # if line.startswith('VALUES'):
        # Ignore commented lines
        if not line.startswith("--") and line.strip("\n"):
            # Append line to the command string, prefix with space
            sql_command += " " + line.strip("\n")
            # sql_command = ' ' + sql_command + line.strip('\n')
        # If the command string ends with ';', it is a full statement
        if sql_command.endswith(";"):
            # Try to execute statement and commit it
            try:
                # print("running " + sql_command+".")
                psql_conn.execute(text(sql_command))
                # psql_conn.commit()
            # Assert in case of error
            except Exception as e:
                print("Error at command:" + sql_command + ".")
                print(e)
                ret_ = False
            # Finally, clear command string
            finally:
                sql_command = ""
                ret_ = True
    return ret_

def run_sql_query_from_file(sql_file, psql_conn):
    sql_command = ""
    ret_ = False
    result = ""
    for line in sql_file:
        # if line.startswith('VALUES'):
        # Ignore commented lines
        if not line.startswith("--") and line.strip("\n"):
            # Append line to the command string, prefix with space
            sql_command += " " + line.strip("\n")
        elif line.startswith("--"):
            # If the command string ends with ';', it is a full statement
            if sql_command.endswith(";"):
                # Try to execute statement and commit it
                try:
                    if sql_command.strip()[:6].lower() == "select":
                        res = pd.read_sql_query(sql_command, psql_conn)
                        result += res.head().to_string() + "\n\n"
                    else:
                        psql_conn.execute(text(sql_command))
                # Assert in case of error
                except Exception as e:
                    print("Error at command:" + sql_command + ".")
                    print(e)
                    ret_ = False
                # Finally, clear command string
                finally:
                    sql_command = ""
                    ret_ = True
            result += line
    if sql_command.endswith(";"):
        # Try to execute statement and commit it
        try:
            if sql_command.strip()[:6].lower() == "select":
                res = pd.read_sql_query(sql_command, psql_conn)
                result += res.head().to_string() + "\n\n"
            else:
                psql_conn.execute(text(sql_command))
        # Assert in case of error
        except Exception as e:
            print("Error at command:" + sql_command + ".")
            print(e)
            ret_ = False
        # Finally, clear command string
        finally:
            ret_ = True
    return ret_, result


def import_data(psql_conn):
    datapath = DATADIR + "\\" + "data.xlsx"      # datapath = DATADIR + "/" + "data.xlsx" for MacBook
    df_xlsx = pd.read_excel(datapath, "city")
    df_xlsx.to_sql("city", con=psql_conn, if_exists="append", index=False)
    df_xlsx = pd.read_excel(datapath, "volunteer")
    df_xlsx.to_sql("volunteer", con=psql_conn, if_exists="append", index=False)
    df_xlsx = pd.read_excel(datapath, "volunteer_range")
    df_xlsx.to_sql("volunteer_range", con=psql_conn, if_exists="append", index=False)
    df_xlsx = pd.read_excel(datapath, "skill")
    df_xlsx.to_sql("skill", con=psql_conn, if_exists="append", index=False)
    df_xlsx = pd.read_excel(datapath, "skill_assignment")
    df_xlsx.to_sql("skill_assignment", con=psql_conn, if_exists="append", index=False)
    df_xlsx = pd.read_excel(datapath, "interest")
    df_xlsx.to_sql("interest", con=psql_conn, if_exists="append", index=False)
    df_xlsx = pd.read_excel(datapath, "interest_assignment")
    df_xlsx.to_sql("interest_assignment", con=psql_conn, if_exists="append", index=False)
    df_xlsx = pd.read_excel(datapath, "beneficiary")
    df_xlsx.to_sql("beneficiary", con=psql_conn, if_exists="append", index=False)
    df_xlsx = pd.read_excel(datapath, "request")
    df_xlsx.to_sql("request", con=psql_conn, if_exists="append", index=False)
    df_xlsx = pd.read_excel(datapath, "request_skill")
    df_xlsx.to_sql("request_skill", con=psql_conn, if_exists="append", index=False)
    df_xlsx = pd.read_excel(datapath, "request_location")
    df_xlsx.to_sql("request_location", con=psql_conn, if_exists="append", index=False)
    df_xlsx = pd.read_excel(datapath, "volunteer_application")
    df_xlsx.to_sql("volunteer_application", con=psql_conn, if_exists="append", index=False)


if __name__ == "__main__":
    DATADIR = str(Path(__file__).parent)  # for relative path
    print(DATADIR)
    database = "group_5_2024"
    user = "group_5_2024"
    password = "f9JsjkRlQee4"
    host = "dbcourse.cs.aalto.fi"
    port = "5432"

    connection = None
    try:
        # Connect to an test database
        connection = psycopg2.connect(
            database=database, user=user, password=password, host=host, port=port
        )
        connection.autocommit = True

        # Create a cursor to perform database operations
        cursor = connection.cursor()
        # Print PostgreSQL details
        print("PostgreSQL server information")
        print(connection.get_dsn_parameters(), "\n")
        # Executing a SQL query
        cursor.execute("SELECT version();")
        # Fetch result
        record = cursor.fetchone()
        print("You are connected to - ", record, "\n")

        DIALECT = "postgresql+psycopg2://"
        db_uri = "%s:%s@%s/%s" % (user, password, host, database)
        print(DIALECT + db_uri)
        engine = create_engine(DIALECT + db_uri, isolation_level="AUTOCOMMIT")
        psql_conn = engine.connect()

        run_sql_from_file(open(DATADIR + "/creating_tables.sql"), psql_conn)
        import_data(psql_conn)

        ret, result = run_sql_query_from_file(open(DATADIR + "/Part_A.sql"), psql_conn)
        print(result)
        psql_conn.commit()

        ret, result = run_sql_query_from_file(open(DATADIR + "/Part_B_a)_b).sql"), psql_conn)
        print(result)
        psql_conn.commit()

        ret, result = run_sql_query_from_file(open(DATADIR + "/Part_B_c).sql"), psql_conn)
        print(result)
        psql_conn.commit()

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if connection:
            connection.close()
            print("PostgreSQL connection is closed")
