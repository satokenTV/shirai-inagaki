# -*- coding: utf-8 -*-
import codecs

class Morpheme:
    def __init__(self,surface,base,pos,pos1):
        self.surface = surface
        self.base = base
        self.pos = pos
        self.pos1 = pos1

class Phrase:
    def __init__(self,morpheme_surfaces,morpheme_bases,morphemes_poses,modifier_index,phrase_index):
        self.morpheme_surfaces = morpheme_surfaces
        self.morpheme_bases = morpheme_bases
        self.morpheme_poses = morphemes_poses
        self.modifier_index = modifier_index
        self.phrase_index = phrase_index

class Sentence:
    def __init__(self, phrases):
        self.phrases = phrases

def init(sentence):
    sentence = Sentence([])

def decisionOutput(phrases):
    output_candidate_phrases = []
    output_candidate_phrases_modifier_indexs = []
    for phrase in phrases:
        for output_candidate_phrase in output_candidate_phrases:
            modifier_index = int(output_candidate_phrase.split("\t")[0])
            modifiee_index = phrase.phrase_index
            if modifier_index == modifiee_index:
                if u"動詞" in phrase.morpheme_poses:
                    noun_particle = output_candidate_phrase.split("\t")[1]
                    verb_index = phrase.morpheme_poses.index(u"動詞")
                    verb = phrase.morpheme_bases[verb_index]
                    verb_noun_particle = verb + ' ' + noun_particle
                    print(verb_noun_particle)
                    output_candidate_phrases.remove(output_candidate_phrase)
                    output_candidate_phrases_modifier_indexs.remove(str(modifier_index))
                    break
        if u"名詞" in phrase.morpheme_poses and u"助詞" in phrase.morpheme_poses:
            noun_index = phrase.morpheme_poses.index(u"名詞")
            noun = phrase.morpheme_surfaces[noun_index]
            particle_index = phrase.morpheme_poses.index(u"助詞")
            particle = phrase.morpheme_surfaces[particle_index]
            if phrase.modifier_index not in output_candidate_phrases_modifier_indexs:
                output_candidate_phrases_modifier_indexs.append(phrase.modifier_index)
                output_candidate_phrases.append(phrase.modifier_index + '\t' + noun + ' ' + particle)
            else:
                index = output_candidate_phrases_modifier_indexs.index(phrase.modifier_index)
                output_candidate_phrases[index] += (' ' + noun + ' ' + particle)


def main():
    input_file = codecs.open("doc0000000000.knp.txt", 'r', "utf-8")
    phrase = Phrase([], [], [], -1, -1)
    sentence = Sentence([])
    phrase_index = 0
# 全体的に変数名見直す
    for line in input_file.readlines():

        if "EOS\n" == line:
            if len(phrase.morpheme_surfaces) != 0:
                sentence.phrases.append(phrase)
            decisionOutput(sentence.phrases)
            sentence = Sentence([])
            phrase_index = 0
            continue
        else:
            line_split = line.split(" ")
            identifiers = []
            identifiers.append(line_split[0])
            identifiers.append(line_split[2][0])
        if '*' == identifiers[0] and '<' == identifiers[1]:
            continue
        if '#' == identifiers[0] and 'U' == identifiers[1]:
            continue
        elif '+' == identifiers[0] and '<' == identifiers[1]:
            if len(phrase.morpheme_surfaces) != 0:
                sentence.phrases.append(phrase)
            #↑1句終わりとしての処理、↓1句はじめとしての処理
            modifier_index = line_split[1][:-1]
            phrase = Phrase([], [], [], modifier_index, phrase_index)
            phrase_index += 1
        else:
            surface = line_split[0]
            base = line_split[2]
            pos = line_split[3]
            phrase.morpheme_surfaces.append(surface)
            phrase.morpheme_bases.append(base)
            phrase.morpheme_poses.append(pos)


    input_file.close()

if __name__ == "__main__":
    main()
