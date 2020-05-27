import pyodbc
import os
from os.path import isfile
from configparser import ConfigParser
from time import sleep

class DatabaseManage(object):
    """
    Before using this component for Database backup or restore, make sure we have below things available in the local machine.
    1) Open VPN connected
    2) Installed pyodbc: >pip install pyodbc
    3) MSSQL database driver installed:
    download link: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver15
    note: Step 2 and 3 are one time effort, but Step 1 should be always in place each time need to use component.
    """
    pyodbc.pooling = False
    _instance = None

    def __new__(cls):
        """db_config = {
            'server': '10.35.10.97',
            'database': 'VertexUserTouhidul',
            'uid': 'sa',
            'pwd': 'SteSysAdmin10#'
        }
        connect_string = 'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={uid};PWD={pwd}'.format(**db_config)
        """
        if cls._instance is None:
            cls._instance = object.__new__(cls)
            db_config = {'DRIVER': '{ODBC Driver 17 for SQL Server}',
                         'SERVER': '10.35.10.97',
                         'UID': 'sa',
                         'PWD': 'SteSysAdmin10#',
                         'Autocommit': True }
            try:
                print('connecting to the database...')
                connection = MSSQLManage._instance.connection = pyodbc.connect(**db_config)
                cursor = MSSQLManage._instance.cursor = connection.cursor()
                cursor.execute('SELECT @@version;')
                db_version = cursor.fetchone()

            except Exception as error:
                print('Error: database connection not successful.')
                #print('Error: database connection not successful. {}'.format(error))
                MSSQLManage._instance = None
            else:
                print('Database connection successful with {}'.format(db_version[0]))
        return cls._instance

    def __init__(self):
        self.connection = self._instance.connection
        self.cursor = self._instance.cursor

    def query(self, sql_query):
        """ execute the query and return the result,
        :return :None when Error
        :return : result when run without error."""
        try:
            result = self.cursor.execute(sql_query)
        except (pyodbc.OperationalError, pyodbc.ProgrammingError) as e:
            print("Error: SQL Query error occured..." +str(e))
            results = None
        except pyodbc.Error as error:
            print('Executing query "{}", error: {}'.format(sql_query, error))
            return None
        else:
            return result

    def backup_database(self, databaseName, backupFileName):
        """ please enter first param the databaseName = MSSQL existing Database Name, which you need to create backup file.
            and 2nd param 'backupFileName' as a backup file name which will be created at SERVER folder location in 'C:\test\AUTO_DB_BACKUPS\,
        :databaseName: 'str'
        :backupFileName: 'str'
        :author: VertexUserTouhidul"""

        if ".bak" in backupFileName.lower():
            backupFileName = backupFileName.split(".")[0]
        else:
            backupFileName = backupFileName
        sql_all_databases = "SELECT name FROM sys.databases WHERE name NOT IN('master','model','msdb','tempdb')"
        # List databases name
        list_databases = self.query(sql_all_databases).fetchall()
        if databaseName in str(list_databases):
            #it will replace the backup file, if you want to append the bak file then use option: WITH NOINIT
            sql_backup_stmt = "SET NOCOUNT ON; BACKUP DATABASE {0} TO  DISK = N'C:/Test/AUTO_DB_BACKUPS/{1}.bak' WITH NOFORMAT, INIT, SKIP, NOREWIND, NOUNLOAD;".format(databaseName, backupFileName)
            try:
                self.query(sql_backup_stmt)
            except pyodbc.Error as error:
                print("Exception:" + str(error))
            else:
                print("Database: {} BACKUP successfully.".format(databaseName))
        else:
            print("Database: {} doesn't exist. Backup can't perform.".format(databaseName))

    def restore_database(self, backupFileName):
        """ please enter the backup file as a parameter,
            Database backup file (.bak) location will at 'C:\test\AUTO_DB_BACKUPS\', in the Database SERVER location not from the local machine.
            make sure Backup file is available before run. Database will be created with pytest.ini.
            it will read the 'GC_ADMIN_USERNAME' value and use as a DATABASE NAME. we don't need to use as a paramerter.
            it will internally read by component.
        :backupFileName: 'str'
        :author: VertexUserTouhidul"""
        #get the database name from pytest.ini file
        databaseName = self.get_GC_UserName()
        if databaseName == None:
            raise NameError("Please update username in your pytest.ini file. RESTORE can't perform...")

        if ".bak" in backupFileName.lower():
            backupFileName = backupFileName.split(".")[0]

        #below sql query restore the database from given backup file
        sql_restore_stmt = """USE master;
        DECLARE @Table TABLE (
            LogicalName varchar(128),
            [PhysicalName] varchar(128),
            [Type] varchar,
            [FileGroupName] varchar(128),
            [Size] varchar(128),
            [MaxSize] varchar(128),
            [FileId] varchar(128),
            [CreateLSN] varchar(128),
            [DropLSN] varchar(128),
            [UniqueId] varchar(128),
            [ReadOnlyLSN] varchar(128),
            [ReadWriteLSN] varchar(128),
            [BackupSizeInBytes] varchar(128),
            [SourceBlockSize] varchar(128),
            [FileGroupId] varchar(128),
            [LogGroupGUID] varchar(128),
            [DifferentialBaseLSN] varchar(128),
            [DifferentialBaseGUID] varchar(128),
            [IsReadOnly] varchar(128),
            [IsPresent] varchar(128),
            [TDEThumbprint] varchar(128),
            [SnapshotUrl] varchar(128)
        )
        DECLARE @Path varchar(200)=N'C:\Test\AUTO_DB_BACKUPS\{0}.bak'
        DECLARE @LogicalNameData varchar(128),@LogicalNameLog varchar(128)
        INSERT INTO @table
        EXEC('RESTORE FILELISTONLY FROM DISK='''+@Path+''' ')
           SET @LogicalNameData=(SELECT LogicalName FROM @Table WHERE Type='D')
           SET @LogicalNameLog=(SELECT LogicalName FROM @Table WHERE Type='L')
        SELECT @LogicalNameData,@LogicalNameLog;
        WAITFOR DELAY '00:00:10';
        RESTORE DATABASE {1} FROM DISK=@Path WITH REPLACE, RECOVERY, NOUNLOAD, STATS = 10,
        MOVE @LogicalNameData TO 'C:\\Program Files\\Microsoft SQL Server\\MSSQL14.GCSTECLOUDQA\\MSSQL\\DATA\\{1}.mdf',
        MOVE @LogicalNameLog TO 'C:\\Program Files\\Microsoft SQL Server\\MSSQL14.GCSTECLOUDQA\\MSSQL\\DATA\\{1}_log.ldf';
        """.format(backupFileName, databaseName)
        print("RESTORE Database processing....")
        try:
            self.drop_database(databaseName)
            sleep(2)
            result = self.query(sql_restore_stmt)
            sleep(30)
            if result == None:
                raise pyodbc.Error("RESTORE Database Failed....")
        except pyodbc.Error as error:
            print("Exception:" + str(error))
        else:
            print("RESTORED Database: '{}' Successful.".format(databaseName))

    def drop_database(self, databaseName):
        """
        Delete Database if exists. user able to delete database with this component and passing database name as a parameter.
        :param: databaseName: type: 'str'
        """
        databaseName = databaseName.strip()
        #sql_drop_db = "DROP DATABASE IF EXISTS {}".format(databaseName)
        sql_drop_database = """IF EXISTS (SELECT name from sys.databases WHERE (name = '{0}'))
                                BEGIN
                                    ALTER DATABASE {0} SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
                                    DROP DATABASE {0};
                                END;""".format(databaseName)
        try:
            #self.query(sql_drop_db)
            self.query(sql_drop_database)
            sleep(5)
        except Exception as e:
            print("Exception:" + str(e))
        else:
            print("DROPPED Database: '{}'.".format(databaseName))

    def create_database(self, databaseName):
        """create new database,
        :param databaseName: type : 'str'
        :return type:None"""
        databaseName = databaseName.strip()
        sql_create_db = """USE master ;
                            CREATE DATABASE {0}
                            ON  PRIMARY
                            ( NAME = N'{0}', FILENAME = N'C:\\Program Files\\Microsoft SQL Server\\MSSQL14.GCSTECLOUDQA\\MSSQL\\DATA\\{0}.mdf' , SIZE = 8MB , FILEGROWTH = 65MB )
                            LOG ON
                            ( NAME = N'{0}_log', FILENAME = N'C:\\Program Files\\Microsoft SQL Server\\MSSQL14.GCSTECLOUDQA\\MSSQL\\DATA\\{0}_log.ldf' , SIZE = 8MB , FILEGROWTH = 65MB );
                            """.format(databaseName)
        try:
            result = self.query(sql_create_db)
            sleep(5)
            if result == None:
                raise pyodbc.Error("Database CREATION Failed....")
        except pyodbc.Error as e:
            print("Exception: " + str(e))
        else:
            print("CREATED Database: '{}'.".format(databaseName))

    def get_GC_UserName(self):
        """this component will read the pytest.ini file and read the 'GC_ADMIN_USERNAME' value from that file.
        :return: username, when find value else None.
        :type: 'str'
        """
        os.getcwd()
        os.chdir('gc-automation/gc_tests')
        pytestFile = 'pytest.ini'
        #print(os.getcwd())
        #print(os.path.isfile('pytest2.ini'))
        try:
            if os.path.isfile(pytestFile):
                print("'{}' file location = {}".format(pytestFile, os.getcwd()))
                configur = ConfigParser()
                configur.read(pytestFile)
                testenv = configur.get('pytest','env')
                username= testenv.partition('GC_ADMIN_USERNAME=')[2].split('\n')[0].strip()
                if(len(username) < 1):
                    print("GC_ADMIN_USERNAME is Empty. please update your 'pytest.ini' file.")
                    return None
                else:
                    return username
            else:
                print("'{}' not found in location = {}".format(pytestFile, os.getcwd()))
                return None
        except OSError:
            print("Error: File could not find.")
            return None

    def __del__(self):
        """this component will close the database connection."""
        self.cursor.close()
        self.connection.close()
        print("Connection closed.")

    def find_company(self, databaseName):
        """ this can be used only for verify the data can fetching from specific database."""
        self.query("USE {}".format(databaseName))
        sql = "SELECT CmpID, Code, Name FROM [dbo].Company"
        #sql ="SELECT CmpID, Code, Name FROM [VertexUserTouhidul].[dbo].Company"
        rows = self.query(sql).fetchall()
        print("=====Fetching Company data=====")
        for row in rows:
            print(row)
            #print(row.CmpID, row.Code, row.Name)
        print("===============================")

    def show_tables(self):
        """ this can be used only for verify the data can fetching from specific database."""
        self.query("USE VertexUserTouhidul;")
        all_tables = self.cursor.tables()
        print(type(all_tables))
        for row in all_tables:
            print(row.table_name)

    def find_driver(self):
        """this component print the local databse driver name on the console."""
        for driver in pyodbc.drivers():
            print(driver)
            print("pyodbc version:" + pyodbc.version)

    def find_hostname(self):
        """this component print the Database server hostname name on the console."""
        hostname = """SELECT @@SERVERNAME AS 'Server Name';"""
        result = self.query(hostname).fetchone()
        if result:
            print("hostname:" + str(result))




db = DatabaseManage()
db.find_driver()
db.find_hostname()
#db.find_company("VertexUserTom")
#=================================
#db.backup_database("VertexUser7650","VertexUser7650")
#db.restore_database("GC_Returns_Setup.bak")
#db.restore_database("GC_Returns_SetupWithData.bak")
#=================================
#db.drop_database("VertexUserTouhidul")
#db.create_database("VertexUserTouhidul")
