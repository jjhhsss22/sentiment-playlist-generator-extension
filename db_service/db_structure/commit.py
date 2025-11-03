# this file only needs to be executed once during initialisation of our db_service
# this will then create our tables on the local sql server

with app.app_context():
    db.create_all()  # creates all tables
    print("Tables committed to the db_service!")