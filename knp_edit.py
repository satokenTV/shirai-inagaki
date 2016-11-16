# -*- coding: utf-8 -*-

def main():
    input_file = open("doc0000000000.knp.txt", "r")
    one_sentence_list = []
    phrase_index_dict = {}
    dependent_index_dict = {}
    morpheme_index = 0
    phrase_index = -1
    dependent_index = 0
    noun_index_list = []
    verb_index_list = []
    particle_index_list = []

    for line in input_file.readlines():
        analysis_morpheme = line.split(" ")
        if "EOS\n" in line:
            if noun_index_list != [] and verb_index_list != [] and particle_index_list != []:
                verb_base = 0
                for verb_index in verb_index_list:
                    if str(phrase_index_dict[verb_index]) in dependent_index_dict:
                        print(one_sentence_list[verb_index], end=' ')
                        for particle_index in dependent_index_dict[str(phrase_index_dict[verb_index])]:
                            if particle_index in particle_index_list:
                                if str(phrase_index_dict[particle_index]) in dependent_index_dict:
                                    noun_index = dependent_index_dict[str(phrase_index_dict[particle_index])][0]
                                    if noun_index in noun_index_list:
                                        print(one_sentence_list[noun_index] + ' ' + one_sentence_list[particle_index] + ' ')
                    print()
            one_sentence_list = []
            phrase_index_dict = {}
            dependent_index_dict = {}
            morpheme_index = 0
            phrase_index = -1
            dependent_index = 0
            noun_index_list = []
            verb_index_list = []
            particle_index_list = []
        elif "+" in analysis_morpheme[0]:
            dependent_index = analysis_morpheme[1].rstrip("D")
            phrase_index += 1
        elif "*" not in analysis_morpheme[0]:
            if "名詞" in analysis_morpheme[3]:
                noun_index_list.append(morpheme_index)
            if "助詞" in analysis_morpheme[3]:
                particle_index_list.append(morpheme_index)
            if "動詞" in analysis_morpheme[3]:
                verb_index_list.append(morpheme_index)
                one_sentence_list.append(analysis_morpheme[2])
            else:
                one_sentence_list.append(analysis_morpheme[0])

            if dependent_index not in dependent_index_dict:
                dependent_index_dict[dependent_index] = []
            dependent_index_dict[dependent_index].append(morpheme_index)

            phrase_index_dict[morpheme_index] = phrase_index
            morpheme_index += 1

    input_file.close()

if __name__ == "__main__":
    main()
