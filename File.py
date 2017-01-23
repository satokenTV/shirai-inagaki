# coding:utf-8
import codecs


class File:
    def __init__(self, place, name):
        self.file_name = place + name

    def get_lines(self):
        file = codecs.open(self.file_name, 'r', "utf-8")
        lines = file.readlines()
        file.close()
        return lines

    def set_lines(self, lines):
        file = codecs.open(self.file_name, 'a', "utf-8")
        for line in lines:
            file.write(line)
        file.close()
        return
