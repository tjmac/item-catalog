#!/usr/bin/python2.7
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import random
import string


db_conn_string = 'postgresql://postgres:meowmix@localhost:5432/catalog'

Base = declarative_base()
secret_key = ''.join(
    random.choice(
        string.ascii_uppercase +
        string.digits) for x in xrange(32))


# User class
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


# Category class with relationships and foreign keys
class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    # added back_populates, setting up many to one
    category_items = relationship("CategoryItem", back_populates="category")

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'items': [i.serialize for i in self.category_items]
        }


# CategoryItem class with relationships and foreign keys
class CategoryItem(Base):
    __tablename__ = 'category_item'

    item_name = Column(String(80), nullable=False)
    item_id = Column(Integer, primary_key=True)
    item_description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    # added back_populates, setting up many to one
    # added cascade='all,delete'
    category = relationship("Category", back_populates="category_items",
                            cascade='all,delete')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.item_name,
            'description': self.item_description,
            'id': self.item_id
        }


engine = create_engine(db_conn_string)

Base.metadata.create_all(engine)
