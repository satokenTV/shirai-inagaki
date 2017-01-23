# -*- coding: utf-8 -*-
import re

import sys

import db
import process_db
import process_file
import kanaconvert
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

_input_file_directory = u""
_input_file_name = u"doc0000000000.knp.txt"
_input_file_place = _input_file_directory + _input_file_name
_db_name = "sqlite:///db.shirai"


def set_phrase_modified(sentence):
    for phrase in sentence.phrases:
        sentence.phrases[phrase.modify_index].modified_indexes.append(phrase.phrase_index)


def check_filtering_particle(particle):
    if particle != u'の' and particle != u'は':
        return False
    else:
        return True


def check_filtering_voice(voice):
    if voice != u"受動" and voice != u"使役":
        return False
    else:
        return True


def check_filtering_adj(phrase):
    takeirenyo_flag = False
    for morpheme in phrase.morphemes:
        if takeirenyo_flag:
            if morpheme.surface == u"ある":
                return True
        takeirenyo_flag = False
        if morpheme.adj == u"タ系連用テ形":
            takeirenyo_flag = True
    return False


def check_connect_verb(phrase, modify_phrase):
    if phrase.modify_index == modify_phrase.phrase_index:
        if phrase.phrase_index == (modify_phrase.phrase_index + 1):
            if phrase.form == u"連用":
                return True
    return False


def decision_output_base(engine):
    sentence_id = 1
    sess = sessionmaker(bind=engine)
    session = sess()

    have_verb_morphemes = session.query(db.Morpheme).filter_by(pos="動詞").all()
    have_noun_morphemes = session.query(db.Morpheme).filter_by(pos="名詞").all()
    have_particle_morphemes = session.query(db.Morpheme).filter_by(pos="助詞").all()
    have_noun_phrase_ids = [morpheme.phrase_id for morpheme in have_noun_morphemes]
    have_particle_phrase_ids = [morpheme.phrase_id for morpheme in have_particle_morphemes]
    have_noun_and_particle_phrase_ids = list(set(have_noun_phrase_ids) & set(have_particle_phrase_ids))

    output_line_list = []

    for have_verb_morpheme in have_verb_morphemes:
        have_verb_phrase = session.query(db.Phrase).filter_by(id=have_verb_morpheme.phrase_id).first()
        have_verb_phrase_modify_phrase = session.query(db.Phrase).filter_by(modify_id=have_verb_phrase.id).all()
        have_verb_phrase_modify_phrase_ids = [phrase.id for phrase in have_verb_phrase_modify_phrase]

        print_noun_and_phrase_phrase_ids = list(
            set(have_noun_and_particle_phrase_ids) & set(have_verb_phrase_modify_phrase_ids))
        output_line = ""
        if print_noun_and_phrase_phrase_ids:
            for print_noun_and_phrase_phrase_id in print_noun_and_phrase_phrase_ids:
                output_line += session.query(db.Morpheme).filter_by(phrase_id=print_noun_and_phrase_phrase_id,
                                                                    pos="名詞").first().surface
                output_line += " "
                output_line += session.query(db.Morpheme).filter_by(phrase_id=print_noun_and_phrase_phrase_id,
                                                                    pos="助詞").first().surface
                output_line += " "
            output_line += have_verb_morpheme.base
            output_line_list.append(output_line)
    print(output_line_list)

def init(surfaces, bases, poses, adjs, modify_ids, voices, forms):
    surfaces = []
    bases = []
    poses = []
    adjs = []
    modify_ids = []
    voices = []
    forms = []
    return surfaces, bases, poses, adjs, modify_ids, voices, forms


def create_db(engine):
    sentences = process_file.get_all_lines(_input_file_place)
    surfaces = []
    bases = []
    poses = []
    adjs = []
    modify_ids = []
    voices = []
    forms = []
    sentence_id = 1

    for sentence in tqdm(sentences):
        sentence = sentence.rstrip()
        if "EOS" == sentence:
            process_db.registration_features(engine, surfaces, bases, poses, adjs, modify_ids, voices, forms,
                                             sentence_id)
            sentence_id += 1
            surfaces, bases, poses, adjs, modify_ids, voices, forms = init(surfaces, bases, poses, adjs, modify_ids,
                                                                           voices, forms)
            continue
        else:
            split_line = sentence.split(" ")
            identifiers = [split_line[0], split_line[2][0]]
        if '*' == identifiers[0] and '<' == identifiers[1]:
            continue
        if '#' == identifiers[0] and 'U' == identifiers[1]:
            continue
        elif '+' == identifiers[0] and '<' == identifiers[1]:
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
                adjs.append('')
        else:
            surfaces.append(split_line[0])
            bases.append(split_line[2])
            poses.append(split_line[3])
            adjs.append(split_line[9])


def main():
    engine = process_db.open_db(_db_name)
    # create_db(engine)
    decision_output_base(engine)


if __name__ == "__main__":
    main()
