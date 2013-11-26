author: karlgrz 
comments: true
date: 2013-03-21 13:40:46
slug: sqlalchemy-deferred-column-loading
title: SQLAlchemy Deferred Column Loading
category: Coding
tags: 2013, orm, python, sqlalchemy

We have a small monitoring [Flask](http://flask.pocoo.org/) web app using [SQLAlchemy](http://www.sqlalchemy.org/) that we use to keep an eye on the status of some jobs in our processing pipeline.

Yesterday we noticed that our DB was getting nailed everytime we refreshed the main status screen, which does NOT show the stack trace (which can be VERY large for big jobs). We needed a way to only pull those fields when they were displayed, but at the same time I didn't want to have a seperate model just to use on the main status screen. What to do?

As of SQLAlchemy 0.8, they offer something called [Deferred column loading](http://docs.sqlalchemy.org/en/latest/orm/mapper_config.html#deferred-column-loading) and it fit the bill nicely! Here's what we had previously that would eager fetch everything:

``` python
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Trace(Base):
	__tablename__ = 'log'

	id = Column(Integer, primary_key=True)
	key = Column(Text)
	created = Column(DateTime)
	failed = Column(Boolean)
	trace = Column(Text)

	def __init__(self, key, created, failed, trace):
		self.key = key
		self.created = created
		self.failed = failed
		self.trace = trace

	def __repr__(self):
		return "<Trace('{0}', '{1}', '{2}', '{3}', '{4}')>".format(self.id, self.key, self.created, self.failed, self.trace)
```

And here's the updated code using deferred column loading:

``` python
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import deferred

Base = declarative_base()

class Trace(Base):
	__tablename__ = 'log'

	id = Column(Integer, primary_key=True)
	key = Column(Text)
	created = Column(DateTime)
	failed = Column(Boolean)
	trace = deferred(Column("trace", Text))

	def __init__(self, key, created, failed, trace):
		self.key = key
		self.created = created
		self.failed = failed
		self.trace = trace

	def __repr__(self):
		return "<Trace('{0}', '{1}', '{2}', '{3}', '{4}')>".format(self.id, self.key, self.created, self.failed, self.trace)
```

Now, the trace column is not loaded until it is used, which is exactly what we were looking for. Nice and clean, too!
