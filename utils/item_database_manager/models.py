from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase, AsyncAttrs):
    ...

class Item(Base):
    __tablename__ = 'items'
    
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, unique=True)
    title = Column(String(64))
    icon_url = Column(Text)
    damage_type = Column(String(64))
    rarity = Column(Integer)

    properties = relationship('Property', back_populates='item', cascade='all, delete-orphan')

    skills = relationship('Skill', back_populates='item', cascade='all, delete-orphan')

    def __str__(self):
        return f'ID: {self.id},\nItem ID: {self.item_id},\nTitle: {self.title},\nIcon URL: {self.icon_url},\nDamage Type: {self.damage_type},\nRarity: {self.rarity}'
    
    
class Property(Base):
    __tablename__ = 'properties'
    
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.item_id'))
    name = Column(String(64))
    value = Column(String(64))

    item = relationship('Item', back_populates='properties')

    def __str__(self):
        return f'{self.name}: {self.value}'


class Skill(Base):
    __tablename__ = 'skills'
    
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.item_id'))
    title = Column(String(64))
    description = Column(Text)
    damage_type = Column(String(64))

    item = relationship('Item', back_populates='skills')
    
    def __str__(self):
        return f'{self.title}[{self.damage_type}]\n{self.description}'
