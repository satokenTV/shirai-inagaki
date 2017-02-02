# -*- coding: utf-8 -*-
import re
import gzip
import time
import os
import db
import process_db
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

_db_name = "sqlite:///db.shirai"


def is_filtering_phrase(voice):
    if voice == "受動" or voice == "使役":
        return False
    return True


def change_surface(verb):
    if verb == "居る" or verb == "煎る" or verb == "射る":
        return "いる"
    return verb


def is_connect_verb_to_verb(morpheme, next_morpheme, session):
    if next_morpheme.pos != "動詞":
        return False

    phrase = session.query(db.Phrase).filter_by(id=morpheme.phrase_id).first()
    next_phrase = session.query(db.Phrase).filter_by(id=next_morpheme.phrase_id).first()

    if phrase.modify_id != next_phrase.id:
        return False

    if phrase.form != "連用":
        return False

    if morpheme.adj == "タ系連用テ形":
        return False

    if morpheme.surface == morpheme.base:
        return False

    return True


def is_connect_noun_to_verb(morpheme, pre_morpheme):
    if morpheme.conjugate != "サ変動詞":
        return False

    if pre_morpheme.pos2 != "サ変名詞":
        return False

    return True


def connect_special_adjective_to_verb(have_special_adjective_phrase_ids, have_special_adjective_morphemes,
                                      modify_verb_phrase_ids):
    special_adjective = ""
    modify_verb_have_special_adjective_phrase_ids = list(
        set(have_special_adjective_phrase_ids) & set(modify_verb_phrase_ids))
    for modify_verb_have_special_adjective_phrase_id in modify_verb_have_special_adjective_phrase_ids:
        for have_special_adjective_morpheme in have_special_adjective_morphemes:
            if have_special_adjective_morpheme.phrase_id == modify_verb_have_special_adjective_phrase_id:
                special_adjective += have_special_adjective_morpheme.surface
    return special_adjective


def connect_adverb_to_verb(have_adverb_phrase_ids, have_adverb_morphemes, modify_verb_phrase_ids):
    adverb = ""
    modify_verb_have_adverb_phrase_ids = list(set(have_adverb_phrase_ids) & set(modify_verb_phrase_ids))
    for modify_verb_have_adverb_phrase_id in modify_verb_have_adverb_phrase_ids:
        for have_special_adjective_morpheme in have_adverb_morphemes:
            if have_special_adjective_morpheme.phrase_id == modify_verb_have_adverb_phrase_id:
                adverb += have_special_adjective_morpheme.surface
    return adverb


def connect_verb_to_verb(have_verb_morpheme, have_verb_next_morpheme, have_verb_pre_morpheme, session):
    verb = ""
    if is_connect_noun_to_verb(have_verb_morpheme, have_verb_pre_morpheme):
        verb += have_verb_pre_morpheme.surface

    if is_connect_verb_to_verb(have_verb_morpheme, have_verb_next_morpheme, session):
        verb += have_verb_morpheme.surface + change_surface(have_verb_next_morpheme.base)
    else:
        verb += change_surface(have_verb_morpheme.base)
    return verb


def decide_output(engine):
    sess = sessionmaker(bind=engine)
    session = sess()

    start = time.time()
    have_noun_morphemes = session.query(db.Morpheme).filter_by(pos="名詞").all()
    have_particle_morphemes = session.query(db.Morpheme).filter_by(pos="助詞").all()
    elapsed_time = time.time() - start
    print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
    exit()
    have_special_particle_morphemes = []
    for special_particle in have_particle_morphemes:  # specialとは"の"と"は"以外の助詞を指す
        if "の" != special_particle.surface and "は" != special_particle.surface:
            have_special_particle_morphemes.append(special_particle)
    have_noun_phrase_ids = [morpheme.phrase_id for morpheme in have_noun_morphemes]
    have_special_particle_phrase_ids = [morpheme.phrase_id for morpheme in have_special_particle_morphemes]
    have_noun_and_particle_phrase_ids = list(set(have_noun_phrase_ids) & set(have_special_particle_phrase_ids))

    have_verb_morphemes = session.query(db.Morpheme).filter_by(pos="動詞").all()
    have_adverb_morphemes = session.query(db.Morpheme).filter_by(pos="副詞").all()
    have_adverb_phrase_ids = [morpheme.phrase_id for morpheme in have_adverb_morphemes]
    have_adjective_morphemes = session.query(db.Morpheme).filter_by(pos="形容詞").all()

    have_special_adjective_morphemes = []
    have_special_adjective_phrase_ids = []
    for special_adjective in have_adjective_morphemes:  # special_adjectiveとはイ形容詞とナ形容詞を含む形容詞を指す
        if "イ形容詞" in special_adjective.conjugate or "ナ形容詞" in special_adjective.conjugate:
            have_special_adjective_morphemes.append(special_adjective)
            have_special_adjective_phrase_ids.append(special_adjective.phrase_id)

    for have_verb_morpheme in tqdm(have_verb_morphemes):
        have_verb_phrase = session.query(db.Phrase).filter_by(id=have_verb_morpheme.phrase_id).first()
        if not is_filtering_phrase(have_verb_phrase.voice):
            continue

        have_verb_pre_morpheme_id = have_verb_morpheme.id - 1
        have_verb_pre_morpheme = session.query(db.Morpheme).filter_by(id=have_verb_pre_morpheme_id).first()
        have_verb_next_morpheme_id = have_verb_morpheme.id + 1
        have_verb_next_morpheme = session.query(db.Morpheme).filter_by(id=have_verb_next_morpheme_id).first()
        if have_verb_next_morpheme is None:
            break

        modify_verb_phrases = session.query(db.Phrase).filter_by(modify_id=have_verb_phrase.id).all()
        modify_verb_phrase_ids = [phrase.id for phrase in modify_verb_phrases]

        print_noun_and_phrase_phrase_ids = list(
            set(have_noun_and_particle_phrase_ids) & set(modify_verb_phrase_ids))
        if print_noun_and_phrase_phrase_ids:
            special_adjective = connect_special_adjective_to_verb(have_special_adjective_phrase_ids,
                                                                  have_special_adjective_morphemes,
                                                                  modify_verb_phrase_ids)
            adverb = connect_adverb_to_verb(have_adverb_phrase_ids, have_adverb_morphemes, modify_verb_phrase_ids)
            verb = connect_verb_to_verb(have_verb_morpheme, have_verb_next_morpheme, have_verb_pre_morpheme, session)
            nouns = ""
            noun_particles = ""
            for print_noun_and_phrase_phrase_id in print_noun_and_phrase_phrase_ids:
                noun = session.query(db.Morpheme).filter_by(phrase_id=print_noun_and_phrase_phrase_id,
                                                            pos="名詞").first().surface
                nouns = nouns + noun + " "
                particle = session.query(db.Morpheme).filter_by(phrase_id=print_noun_and_phrase_phrase_id,
                                                                pos="助詞").first().surface
                noun_particles = noun_particles + noun + " " + particle + " "
                verb = adverb + special_adjective + verb
                session = process_db.registration_result_c(session, noun, particle, verb)
            session = process_db.registration_result_ab(session, nouns, noun_particles, verb)
    session.commit()


def create_db(engine):
    surfaces, bases, poses, pos2s, conjugates, adjs, modify_ids, voices, forms = ([], [], [], [], [], [], [], [], [])
    sess = sessionmaker(bind=engine)
    session = sess()
    sentence_id = 1

    folder_numbers = ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15"]
    for folder_number in tqdm(folder_numbers, ascii=True, desc="folder"):
        gz_file_directory = u"www/tsubame" + folder_number + ".kototoi.org/"
        file_names = os.listdir(gz_file_directory)
        for file_name in tqdm(file_names, ascii=True, desc="file"):
            with gzip.open(gz_file_directory + file_name, 'r') as gz:
                for sentence in tqdm(gz.readlines(), ascii=True, desc="sentence", miniters=50000):
                    sentence = sentence.decode("euc_jp", "ignore")
                    sentence = sentence.rstrip()
                    if "EOS" == sentence:
                        session = process_db.registration_features(session, surfaces, bases, poses, pos2s, conjugates, adjs,
                                                                   modify_ids, voices, forms, sentence_id)
                        sentence_id += 1
                        surfaces, bases, poses, pos2s, conjugates, adjs, modify_ids, voices, forms = (
                            [], [], [], [], [], [], [], [], [])
                        continue
                    else:
                        split_line = sentence.split(" ")
                        if split_line[0] == "":
                            split_line[0] = "・"
                            split_line[1] = "・"
                            split_line[2] = "・"
                        identifiers = [split_line[0], split_line[1][0], split_line[2][0]]
                    if '*' == identifiers[0] and '<' == identifiers[2]:
                        continue
                    if '#' == identifiers[0] and 'S' == identifiers[1]:
                        continue
                    elif '+' == identifiers[0] and '<' == identifiers[2]:
                        modify_ids.append(int(split_line[1][:-1]))
                        if re.findall(r"<態:(.*?)>", sentence):
                            voices.append(re.findall(r"<態:(.*?)>", sentence)[0])
                        else:
                            voices.append(' ')
                        if re.findall(r"<係:(.*?)>", sentence):
                            forms.append(re.findall(r"<係:(.*?)>", sentence)[0])
                        else:
                            forms.append('')

                        if surfaces:
                            surfaces.append('')
                            bases.append('')
                            poses.append('')
                            pos2s.append('')
                            conjugates.append('')
                            adjs.append('')
                    else:
                        surfaces.append(split_line[0])
                        bases.append(split_line[2])
                        poses.append(split_line[3])
                        pos2s.append(split_line[5])
                        conjugates.append(split_line[7])
                        adjs.append(split_line[9])
        session.commit()


def main():
    engine = process_db.open_db(_db_name)
    create_db(engine)
    # decide_output(engine)


if __name__ == "__main__":
    main()
