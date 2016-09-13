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
		String(500), nullable = False)
	email = Column (
		String(500), nullable = False)
	picture = Column (
		String(10000))
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
		String(500), nullable = False)
	id = Column (
		Integer, primary_key = True)
	text = Column (
		String(200000))
	tagline = Column (
		String(1000))
	date = Column (
		String(50))
	last_edited = Column (
		String(50))
	picture = Column (
		String(25000))
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
			'author' : self.user.name,
			'date' : self.date,
			'last_edited' : self.last_edited,
			'user_id' : self.user_id,
		}

# Class
class Comment (Base):

	# Table Info
	__tablename__ = 'comment'
	# Mappers
	id = Column (
		Integer, primary_key = True)
	text = Column (
		String(20000))
	date = Column (
		String(50))
	last_edited = Column (
		String(50))
	user_id = Column (
		Integer, ForeignKey('user.id'))
	user = relationship(User)
	article_id = Column (
		Integer, ForeignKey('article.id'))
	article = relationship(Article)
	# JSON
	@property
	def serialize(self):
		return {
			'id' : self.id,
			'text' : self.text,
			'author' : self.user.name,
			'article' : self.article.title,
			'date' : self.date,
			'last_edited' : self.last_edited,
		}

# Configuration
engine = create_engine('postgresql://catalog:2;8[%FtUWE@opQ$?6TddBm)4@localhost/catalog')
Base.metadata.create_all(engine)
