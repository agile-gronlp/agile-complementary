# This script extracts entries from the LSJ and writes the resulting list to a file.

import pickle
import config
from cltk.alphabet.grc import grc  # For normalizing texts
import glob
import xml.etree.ElementTree as ET
import re


def main():

    files = glob.glob('LSJ_GreekUnicode' + "/*.xml")
    lexicon = []
    # Add entries from LSJ
    for file in files:
        tree = ET.parse(file)
        entries = tree.findall(".//entryFree")
        for entry in entries:
            key = re.sub('[0-9]', '', entry.attrib['key'])  # Remove numbers after key
            lexicon.append(grc.normalize_grc(key.lower()))
    # Add lemmas from train
    with open(destination_train_path, 'r') as f:
        for line in f:
            if re.match('^[0-9]+', line):  # id
                lemma = grc.normalize_grc(line.split('\t')[2])
                if lemma not in lexicon:
                    lexicon.append(lemma)
                else:
                    lexicon.remove(lemma)
                    lexicon.append(lemma)  # For order

    lexicon = list(reversed(lexicon))
    pickle.dump(lexicon, open("../evaluate/lexicon.p", "wb"))


main()
