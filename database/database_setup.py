#! /usr/bin/env python3

import sys

from sqlalchemy import Column, ForeignKey, Integer, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

# Create database structure

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key = True)
    email = Column(String(250), nullable = False)
    name = Column(String(250), nullable = False)
    avatar = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            "name" : self.name,
            "id" : self.id,
            "email" : self.email,
            "avatar" : self.avatar,
        }

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    items = relationship("Item", lazy='subquery', back_populates="category")

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            "name" : self.name,
            "id" : self.id,
            "items" : self.items 
        }

    
class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    content = Column(String(5000))
    created_at = Column(BigInteger, nullable = False)
    updated_at = Column(BigInteger, nullable = False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship("Category", back_populates = "items")

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            "name" : self.name,
            "id" : self.id,
            "content" : self.content
        }


if __name__ == '__main__':
    engine = create_engine('sqlite:///catalog.db')

    Base.metadata.create_all(engine)

    # Initialize data for database

    Base.metadata.bind = engine
    DBSession = sessionmaker(bind = engine)
    session = DBSession()
    soccer_category = Category(name = "Soccer")
    basketball_category = Category(name = "Basketball")
    baseball_category = Category(name = "Baseball")
    frisbee_category = Category(name = "Frisbee")
    snowboarding_category = Category(name = "Snowboarding")
    rock_climbing_category = Category(name = "Rock Climbing")
    football_category = Category(name = "Football")
    skating_category = Category(name = "Skating")
    hockey_category = Category(name = "Hockey")
    session.add(soccer_category);
    session.add(basketball_category);
    session.add(baseball_category);
    session.add(frisbee_category);
    session.add(snowboarding_category);
    session.add(rock_climbing_category);
    session.add(football_category);
    session.add(skating_category);
    session.add(hockey_category);
    session.commit()

