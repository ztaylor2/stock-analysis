"""Model for database of users and passwords."""

from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    Unicode
)

from .meta import Base


class User(Base):
    """Model of user/pass info in DB."""

    __tablename__ = 'users'
    id = Column(Integer)
    username = Column(Text, primary_key=True)
    password = Column(Text)

    def __repr__(self):
        """Return LJ id."""
        return '<{}, {}>'.format(self.username, self.password)


Index('my_index', User.username, unique=True, mysql_length=255)


class Portfolio(Base):
    """Create DB for unique user stock portfolio."""

    __tablename__ = 'portfolio'
    username = Column(Text, primary_key=True)
    stocks = Column(Unicode)
