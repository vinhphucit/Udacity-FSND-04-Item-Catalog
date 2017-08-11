from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.database_setup import Base, Category, Item, User
import time,datetime
class DatabaseManager:

    """ This class contains method used for getting data from sqlite """

    # Get session to be able to access sqlite database
    def get_session(self):
        engine = create_engine("sqlite:///catalog.db")
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind = engine)
        session = DBSession()
        return session

    def create_user(self, name, email, avatar):
        new_user = User(name = name, email = email, avatar = avatar)
        session = self.get_session();
        session.add(new_user)
        session.commit();
        user = session.query(User).filter_by(email=email).one()
        return user.id

    def get_user_id(self, email):
        try:
            session = self.get_session();
            user = session.query(User).filter_by(email=email).one()
            return user.id
        except:
            return None

    def get_user_info(self, user_id):
        session = self.get_session();
        user = session.query(User).filter_by(id = user_id).one()
        return user

    def get_categories(self):
        session = self.get_session();
        categories = session.query(Category).outerjoin(Category.items).all()
        return categories

    def get_latest_items(self):
        session = self.get_session()
        items = session.query(Item).join(Item.category).order_by(Item.created_at.desc()).limit(20)
        return items

    def get_items_count(self, category_id):
        session = self.get_session()
        return session.query(Item).filter(Item.category_id == category_id).count()

    def get_items(self, category_id):
        session = self.get_session()
        items = session.query(Item).join(Item.category).filter(Item.category_id == category_id)
        return items

    def get_item(self, item_id):
        session = self.get_session()
        item = session.query(Item).filter(Item.id == item_id).one()
        return item

    def create_items(self, category_id, name, description, user_id):
        session = self.get_session()
        current_time = time.mktime(datetime.datetime.now().timetuple()) * 1000
        item = Item(name = name, content = description, category_id = category_id, created_at = current_time, updated_at = current_time, user_id = user_id)
        session.add(item)
        session.commit()

    def update_item(self, itemid, itemname, itemcontent, category_id):
        session = self.get_session()
        item = session.query(Item).filter(Item.id == itemid).one()
        item.name = itemname
        item.content = itemcontent
        item.category_id = category_id
        print(itemcontent)
        session.add(item)
        session.commit()
        return item

    def delete_item(self, itemid):
        session = self.get_session()
        item = session.query(Item).filter(Item.id == itemid).one()
        session.delete(item)
        session.commit()
