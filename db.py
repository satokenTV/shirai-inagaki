# coding:utf-8
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import backref, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Sentence(Base):
    __tablename__ = "sentences"
    id = Column(Integer, primary_key=True, nullable=False)
    strings = Column(String, nullable=False )    # Sentenceの持つ文字列
    phrases = relationship("Phrase", backref="sentence")    # Phraseテーブルと関連を持たせる
    # backrefの値は,何でも良い(このテーブル名である必要はない)


class Phrase(Base):
    __tablename__ = "phrases"
    id = Column(String, primary_key=True, nullable=False)
    modify_id = Column(String, nullable=False)  # 係り先のphrase_id
    voice = Column(String, nullable=False)  # 受動態や使役態など、態の種類
    form = Column(String, nullable=False)
    sentence_id = Column(Integer, ForeignKey("sentences.id"), nullable=False)    # Sentenceテーブルを参照するための外部キー
    morphemes = relationship("Morpheme", backref="phrase")  # Morphemeテーブルと関連を持たせる


class Morpheme(Base):
    __tablename__ = "morphemes"
    id = Column(Integer, primary_key=True, nullable=False)
    surface = Column(String, nullable=False)    # 表層形
    base = Column(String, nullable=False)   # 原型
    pos = Column(String, nullable=False)    # 品詞
    pos2 = Column(String, nullable=False)  # 品詞細分類
    conjugate = Column(String, nullable=False)  # 活用形
    adj = Column(String, nullable=False)    # 連用,連体の情報
    phrase_id = Column(String, ForeignKey("phrases.id"), nullable=False)  # Phraseテーブルを参照するための外部キー
