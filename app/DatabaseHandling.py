def read_credientals(source_credentials,target):
     # Retrieve the source database credentials from the form fields
            source_database_host = source_credentials.get("source-database-host")
            source_database_name = source_credentials.get("source-database-name")
            source_database_username = source_credentials.get("source-database-username")
            source_database_password = source_credentials.get("source-database-password")

            for k,v in source_credentials.items():
                    print(k,v)

            print(source_database_host)
            print(source_database_name)
            print(source_database_username)
            print(source_database_password)
