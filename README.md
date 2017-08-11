# Item Catalog Web App

This website is fourth project in FSND Course

### About Project

This project used Python and some techniques and technologies to build a simple website and api. This website connected into Sqlite to get data and data from SQLite was converted to Object Model using sqlalchemy. To be able to create new Item or Detete or Modify Item, user has to login to system using Google OAuth.

### Technologies
1. Python 3.x
2. Flask
3. CSS
4. HTML
5. Google OAuth
6. SQLite
7. SQLAlchemy

### Installation
1. Install Vagrant, VirtualBox and Python as previous project (I used python 3 in this project)
2. Clone project's source code and copy to Vagrant's shared folder
3. Start vagrant with `vagrant up`
4. Login into Vagrant and navigate to Shared Folder, usually it's `/vagrant` in the Vagrant Virtual Machine
5. In the project folder run this command to initialize SQLite database `python3 ./database/database_setup.py`
6. Start Web app with this command `python3 ./application.py`
7. Open browser and access url: [http://localhost:8080](http://localhost:8080)

### JSON Endpoints
In this project I provided 4 JSON Endpoints
1. Get All categories 
[http://localhost:8080/catalog/JSON](http://localhost:8080/catalog/JSON)
2. Get Latest Items
[http://localhost:8080/items/JSON](http://localhost:8080/items/JSON)
3. Get list of items in specific category
[http://localhost:8080/categories/1/items/JSON](http://localhost:8080/categories/1/items/JSON)
4. Get specific item by id
[http://localhost:8080/items/1/JSON](http://localhost:8080/items/1/JSON)

### Note
Please notice that I created some default categories, you will not see any items at the beginning, please login and fell free to create as many items as you want.
