from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class HoldingTable(Base):
    __tablename__ = 'holdings'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    quandl_ref = Column(String)
    price_col = Column(String)

    def __str__(self):
        return f'{self.name} (data from quandl {self.quandl_ref})'

    def __repr__(self):
        return f'HoldingTable(id={self.id}, name={self.name}, quandl_ref={self.quandl_ref}, price_col={self.price_col})'
