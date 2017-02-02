# coding:utf-8
import codecs


def get_all_lines(_input_file_place):
    input_file = codecs.open(_input_file_place, 'r', "utf-8")
    return input_file.readlines()

