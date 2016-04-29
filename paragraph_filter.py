import os
import re
import sys
from nltk.corpus import stopwords
import csv


def create_index(data_dir):

    if not os.path.isdir('output'):
        os.makedirs('output')

    term_dict = {}
    files = os.listdir(data_dir)
    counter = 0
    for file in files:
        counter += 1
        print("%d/%d" % (counter, len(files)), end='\r')
        if '.html' in file:
            f = open(data_dir + '/' + file, 'r')
            readfile = f.read()
            p = re.compile('<.*?>')
            li = p.findall(readfile)
            for instance in li:
                readfile = readfile.replace(instance, '')
            p = re.compile('\[[0-9]*?\]|/|\.|\(|\)|,|\"|\−|\;|\[|\]|\*|\:|\~')
            li = p.findall(readfile)
            for instance in li:
                readfile = readfile.replace(instance, '')
            words_rep = readfile.split()
            words_rep = [word.lower() for word in words_rep]
            words = []
            for i in words_rep:
                if i not in words:
                    words.append(i)
            stop = stopwords.words('english')
            for word in words:
                if word in stop:
                    continue
                elif word in term_dict:
                    term_dict[word].append(file)
                else:
                    term_dict[word] = [file]
    keys = open("keys", "w")
    for key, val in term_dict.items():
        if len(key.encode('utf-8')) <= 255:
            w = csv.writer(open("output/" + key + ".csv", "w"))
            w.writerow(val)
            keys.write(key+"\n")


if __name__ == '__main__':
    source_dir = sys.argv[1]
    create_index(source_dir)
