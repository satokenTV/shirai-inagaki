# coding:utf-8
import db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def open_db(db_name):
    engine = create_engine(db_name, echo=True)
    db.Base.metadata.create_all(engine)

    return engine


def registration_features(engine, surfaces, bases, poses, pos2s, conjugates, adjs, modify_ids, voices, forms,
                          sentence_id):
    sess = sessionmaker(bind=engine)
    session = sess()
    session.add(db.Sentence(strings=''.join(surfaces)))
    phrase_id = 1
    for modify_id, voice, form in zip(modify_ids, voices, forms):
        phrase_id_str = str(sentence_id) + '.' + str(phrase_id)
        modify_index_str = str(sentence_id) + '.' + str(modify_id + 1)
        session.add(
            db.Phrase(id=phrase_id_str, modify_id=modify_index_str, voice=voice, form=form, sentence_id=sentence_id))
        phrase_id += 1

    phrase_id = 1
    phrase_id_str = str(sentence_id) + '.' + str(phrase_id)
    for surface, base, pos, pos2, conjugate, adj in zip(surfaces, bases, poses, pos2s, conjugates, adjs):
        if surface == '' and base == '' and pos == '' and pos2 == '' and conjugate == '' and adj == '':
            phrase_id += 1
            phrase_id_str = str(sentence_id) + '.' + str(phrase_id)
        else:
            session.add(db.Morpheme(surface=surface, base=base, pos=pos, pos2=pos2, conjugate=conjugate, adj=adj,
                                    phrase_id=phrase_id_str))

    session.commit()

    return True
