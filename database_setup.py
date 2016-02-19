# Configuration
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


# Class
class User (Base):

	# Table Info
	__tablename__ = 'user'
	# Mappers
	name = Column (
		String(250), nullable = False)
	email = Column (
		String(250), nullable = False)
	picture = Column (
		String(250))
	id = Column (
		Integer, primary_key = True)
	# JSON
	@property
	def serialize(self):
		return {
		'name': self.name,
		'email': self.email,
		'id' : self.id,
		}



# Class
class Category (Base):

	# Table Info
	__tablename__ = 'category'
	# Mappers
	name = Column (
		String(80), nullable = False)
	id = Column (
		Integer, primary_key = True)
	user_id = Column (
		Integer, ForeignKey('user.id'))
	user = relationship(User)
	# JSON
	@property
	def serialize(self):
		return {
			'name' : self.name,
			'id' : self.id,
			'user_id' : self.user_id,
		}

# Class
class Article (Base):

	# Table Info
	__tablename__ = 'article'
	# Mappers
	title = Column (
		String(80), nullable = False)
	id = Column (
		Integer, primary_key = True)
	text = Column (
		String(2000))
	tagline = Column (
		String(100))
	author = Column (
		String(80))
	date = Column (
		String(25))
	picture = Column (
		String(250))
	category_id = Column (
		Integer, ForeignKey('category.id'))
	category = relationship(Category)
	user_id = Column (
		Integer, ForeignKey('user.id'))
	user = relationship(User)
	# JSON
	@property
	def serialize(self):
		return {
			'id' : self.id,
			'category_id' : self.category_id,
			'title' : self.title,
			'tagline' : self.tagline,
			'text' : self.text,
			'author' : self.author,
			'date' : self.date,
			'user_id' : self.user_id,
		}

# Configuration
engine = create_engine('sqlite:///newspaper.db')
Base.metadata.create_all(engine)