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


def is_voice_filtering_(phrase):
    if phrase.voice == "受動" or phrase.voice == "使役":
        return True
    return False


def decision_output_base(engine):
    sess = sessionmaker(bind=engine)
    session = sess()

    have_verb_morphemes = session.query(db.Morpheme).filter_by(pos="動詞").all()

    output_line_list = []

    for have_verb_morpheme in have_verb_morphemes:
        have_verb_phrase = session.query(db.Phrase).filter_by(id=have_verb_morpheme.phrase_id).first()
        if is_voice_filtering_(have_verb_phrase):
            continue
        have_verb_pre_morpheme_id = have_verb_morpheme.id - 1
        have_verb_2_pre_morpheme_id = have_verb_morpheme.id - 2
        have_verb_pre_morpheme = session.query(db.Morpheme).filter_by(id=have_verb_pre_morpheme_id).first()
        have_verb_2_pre_morpheme = session.query(db.Morpheme).filter_by(id=have_verb_2_pre_morpheme_id).first()

        if have_verb_pre_morpheme.pos == "助詞" and have_verb_2_pre_morpheme.pos == "名詞":
            noun = have_verb_2_pre_morpheme.surface
            particle = have_verb_pre_morpheme.surface
            verb = have_verb_morpheme.base
            output_line_list.append(noun + ' ' + particle + ' ' + verb)

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
