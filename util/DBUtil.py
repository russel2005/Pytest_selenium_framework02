import os
from time import sleep
if os.name == 'posix':
    pass
elif os.name == 'nt':
    import pyodbc
else:
    assert False, "os not recognized in env.py"


sql_connection = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=10.35.10.97;UID=sa;PWD=SteSysAdmin10#'


class DatabaseUtil(object):

    def __init__(self, connection_string=(sql_connection)):

        self.connection_string = connection_string
        self.connector = None

    def __enter__(self):

        self.connector = pyodbc.connect(self.connection_string)
        self.connector.autocommit = True
        self.cursor = self.connector.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):

        if exc_tb is None:
            self.connector.commit()
        else:
            self.connector.rollback()
        self.connector.close()


    def restore(self, database):

        """Restores the given database to the environment indicated in pytest.ini for GC_ADMIN_USERNAME
           Must be connected to OpenVPN

        : param database : Name of the database to restore (Ex: GC_Returns_SetupForReportGen)"""

        gcUser = os.getenv("GC_ADMIN_USERNAME")
        if gcUser == None:
            raise NameError("GC_ADMIN_USERNAME cannot be blank in pytest.ini file")

        with DatabaseUtil() as cursor:
            print ("Drop database from ", gcUser)
            try:
                drop = cursor.execute(self._drop_database(gcUser))
                while cursor.nextset():
                    pass
            except pyodbc.Error as error:
                raise Exception ("Database drop failed with the following error: {}".format(error))
                return None
            else:
                print ("Database drop complete")

            sleep(5)
            print ("Restore database ", database)
            try:
                restore = cursor.execute(self._restore_database(database, gcUser))
                while cursor.nextset():
                    pass
            except pyodbc.Error as error:
                raise Exception ("Database restore failed with the following error: {}".format(error))
                return None
            else:
                print ("Restore complete")

    ############################
    #   Internal Components    #
    ############################

    def _drop_database(self, databaseName):
        """Drops the data given"""

        sql_drop_database = """IF EXISTS (SELECT name from sys.databases WHERE (name = '{0}'))
                                BEGIN
                                    ALTER DATABASE {0} SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
                                    DROP DATABASE {0};
                                END;""".format(databaseName)
        return sql_drop_database

    def _restore_database(self, backupName, databaseName):
        """SQL script to restore the given database"""

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
        DECLARE @Path varchar(200)='C:\\Test\\AUTO_DB_BACKUPS\\{0}.bak'
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
        """.format(backupName, databaseName)
        return sql_restore_stmt
