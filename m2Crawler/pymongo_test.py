from pymongo import MongoClient
import traceback

host = 'localhost'
port = 27017


def main():
    try:
        client = MongoClient(
            host=host,
            port=port
            # replica=replica set
            # username=user
            # password=password
            # authSource=auth database
        )
        names = client.list_database_names();
        print(names);
        db = client['example']  ## db name
        collections = db.list_collection_names();
        print(collections)

        cursor = db.rating.find()
        print(len(list(cursor)))


        print('MongoDB Connected.')
    except Exception as e:
        print(traceback.format_exc())
    finally:
        client.close()
        print('MongoDB Closed.')


if __name__ == "__main__":
    main()