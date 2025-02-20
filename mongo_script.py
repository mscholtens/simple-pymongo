import pymongo
from pymongo import MongoClient
import re

# Establish connection to MongoDB running on Minikube
client = MongoClient('mongodb://localhost:27017/')

# Set the initial active database
current_db = None
current_collection = None

def test_connection():
    """Test the connection to MongoDB service."""
    try:
        # Attempt a simple operation to check if MongoDB is reachable
        client.admin.command('ping')
        print(f"Successfully connected to MongoDB at: mongodb://localhost:27017/")
    except pymongo.errors.ConnectionError as e:
        print(f"Error: Could not connect to MongoDB service. {e}")

def list_databases():
    """List all databases in MongoDB."""
    databases = client.list_database_names()
    print("Databases:", databases)

def add_database(db_name):
    """Create a new database (actually just switch to it and it will be created when a collection is added)."""
    global current_db
    current_db = client[db_name]
    print(f"Database '{db_name}' selected.")

def update_database_name(old_name, new_name):
    """Rename a database (MongoDB doesn't allow direct renaming of databases)."""
    if old_name not in client.list_database_names():
        print(f"Database '{old_name}' does not exist.")
        return

    old_db = client[old_name]
    new_db = client[new_name]

    for collection_name in old_db.list_collection_names():
        collection = old_db[collection_name]
        new_db.create_collection(collection_name, collection_options=collection.options())
        new_db[collection_name].insert_many(collection.find())

    client.drop_database(old_name)
    print(f"Database '{old_name}' renamed to '{new_name}'.")

def remove_database(db_name):
    """Remove a database."""
    if db_name in client.list_database_names():
        client.drop_database(db_name)
        print(f"Database '{db_name}' removed.")
    else:
        print(f"Database '{db_name}' not found.")

def switch_database(db_name):
    """Switch to a different database."""
    global current_db
    if db_name in client.list_database_names():
        current_db = client[db_name]
        print(f"Switched to database '{db_name}'.")
    else:
        print(f"Database '{db_name}' does not exist.")

def list_collections():
    """List all collections in the current database."""
    if current_db is not None:
        collections = current_db.list_collection_names()
        if collections:
            print("Collections:", collections)
        else:
            print("No collections found in the current database.")
    else:
        print("No database selected.")

def add_collection(collection_name):
    """Add a new collection to the current database."""
    if current_db is not None:
        current_db.create_collection(collection_name)
        print(f"Collection '{collection_name}' added to the database.")
    else:
        print("No database selected.")

def remove_collection(collection_name):
    """Remove a collection from the current database."""
    if current_db is not None:
        if collection_name in current_db.list_collection_names():
            current_db.drop_collection(collection_name)
            print(f"Collection '{collection_name}' removed.")
        else:
            print(f"Collection '{collection_name}' does not exist in the current database.")
    else:
        print("No database selected.")

def change_entry(collection_name, query, update_data):
    """Change an entry in a collection."""
    if current_db is not None:
        collection = current_db[collection_name]
        result = collection.update_one(query, {"$set": update_data})
        if result.modified_count > 0:
            print(f"Entry updated in '{collection_name}' collection.")
        else:
            print("No entries were modified.")
    else:
        print("No database selected.")

def add_entry(collection_name, entry_data):
    """Add a new entry to a collection."""
    if current_db is not None:
        collection = current_db[collection_name]
        collection.insert_one(entry_data)
        print(f"New entry added to '{collection_name}' collection.")
    else:
        print("No database selected.")

def remove_entry(collection_name, query):
    """Remove an entry from a collection."""
    if current_db is not None:
        collection = current_db[collection_name]
        result = collection.delete_one(query)
        if result.deleted_count > 0:
            print(f"Entry deleted from '{collection_name}' collection.")
        else:
            print("No entries found to delete.")
    else:
        print("No database selected.")

def list_entries(collection_name):
    """List all entries in a collection."""
    if current_db is not None:
        collection = current_db[collection_name]
        entries = collection.find()
        for entry in entries:
            print(entry)
    else:
        print("No database selected.")

def choice_menu():
    """Display the choice menu and handle user input."""
    global current_db, current_collection
    while True:
        print("\nChoose an option (type 'quit' to exit):")
        print("1. List all databases")
        print("2. Add a new database")
        print("3. Update database name")
        print("4. Remove a database")
        print("5. Switch to a different database")
        print("6. List collections in the current database")
        print("7. Add a new collection to the current database")
        print("8. Remove a collection from the current database")
        print("9. Add a new entry to a collection")
        print("10. Change an entry in a collection")
        print("11. Remove an entry from a collection")
        print("12. List all entries in a collection")
        print("13. Test connection to MongoDB service")

        choice = input("Enter your choice (1-13 or 'quit' to exit): ").strip()

        if choice == 'quit':
            print("Exiting the program...")
            break
        elif choice == '1':
            list_databases()
        elif choice == '2':
            db_name = input("Enter the new database name: ")
            add_database(db_name)
        elif choice == '3':
            old_name = input("Enter the old database name: ")
            new_name = input("Enter the new database name: ")
            update_database_name(old_name, new_name)
        elif choice == '4':
            db_name = input("Enter the database name to remove: ")
            remove_database(db_name)
        elif choice == '5':
            db_name = input("Enter the database name to switch to: ")
            switch_database(db_name)
        elif choice == '6':
            list_collections()
        elif choice == '7':
            collection_name = input("Enter the collection name to add: ")
            add_collection(collection_name)
        elif choice == '8':
            collection_name = input("Enter the collection name to remove: ")
            remove_collection(collection_name)
        elif choice == '9':
            collection_name = input("Enter the collection name: ")
            entry_data = input("Enter the entry data (e.g., name:John, age:30): ").split(",")
            entry_dict = {field.split(":")[0].strip(): field.split(":")[1].strip() for field in entry_data}
            add_entry(collection_name, entry_dict)
        elif choice == '10':
            collection_name = input("Enter the collection name: ")
            query = input("Enter the query to match the entry (e.g., name:John): ").split(",")
            query_dict = {field.split(":")[0].strip(): field.split(":")[1].strip() for field in query}
            update_data = input("Enter the fields to update (e.g., age:31): ").split(",")
            update_dict = {field.split(":")[0].strip(): field.split(":")[1].strip() for field in update_data}
            change_entry(collection_name, query_dict, update_dict)
        elif choice == '11':
            collection_name = input("Enter the collection name: ")
            query = input("Enter the query to match the entry (e.g., name:John): ").split(",")
            query_dict = {field.split(":")[0].strip(): field.split(":")[1].strip() for field in query}
            remove_entry(collection_name, query_dict)
        elif choice == '12':
            collection_name = input("Enter the collection name: ")
            list_entries(collection_name)
        elif choice == '13':
            test_connection()
        else:
            print("Invalid choice! Please enter a valid number (1-13) or 'quit'.")

if __name__ == "__main__":
    choice_menu()
