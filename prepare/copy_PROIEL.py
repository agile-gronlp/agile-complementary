# This script creates the train, development and test set from the
# PROIEL files to train an Ancient Greek lemmatizer using Stanza.

from cltk.alphabet.grc import grc  # For normalizing texts
import config  # For corpus filepaths
import sys  # For feedback
import re


def copy_split(destination_path, proiel_path):
    """
    Copies the data from the PROIEL split to another file.
    :param destination_path: path to write the data to (str)
    :param proiel_path: PROIEL path (str)
    :return: actual number of printed lemmas (int)
    """

    lemmas = 0
    with open(proiel_path) as p_f, open(destination_path, "a") as c_p:
        for line in p_f:
            line = re.sub('\([^)]*\)', '', line)  # Remove text within brackets (e.g. οὕτω(ς) -> οὕτω)
            # Add custom rules (chars have been normalized)
            line = re.sub('[Ϝϝh]', '', line)
            line = re.sub('(κς)|(κσ)|(χς)|(χσ)', 'ξ', line)
            line = re.sub('(Κς)|(Κσ)|(Χσ)|(Χς)', 'Ξ', line)
            line = re.sub('(φς)|(φσ)', 'ψ', line)
            line = re.sub('(Φς)|(Φσ)', 'Ψ', line)
            line = re.sub(' [|∣·∙∶:,.⁝⋮⁞⁙“”]+', '', line)
            c_p.write(grc.normalize_grc(line))
            if line != "\n" and not line.startswith('#'):
                lemmas += 1
        return lemmas


def main():

    print("Printed", copy_split(config.destination_train_path, config.proiel_train_path), "lemmas to train.", file=sys.stderr)
    print("Printed", copy_split(config.destination_dev_path, config.proiel_dev_path), "lemmas to dev.", file=sys.stderr)
    print("Printed", copy_split(config.destination_test_path, config.proiel_test_path), "lemmas to test.", file=sys.stderr)


main()
