# This script evaluates AGILe.

import sys  # To import split_CGRN
sys.path.append('../prepare/')
from split_CGRN import *
import stanza
from nltk import ngrams
import pickle
from string import punctuation
from Levenshtein import distance
from agile import lemmatize


def main():

    file_scores = dict()
    corr_total = incorr_total = 0
    with open(config.destination_test_path) as f:
        for line in f:
            # Print metadata
            if line.startswith('# source'):
                source = line[11:].rstrip()
                # Reset words, lemmata and counts
                words, lemmata = [], []
                corr_in_file = incorr_in_file = 0
            elif line.startswith('# text'):
                original_text = ' '.join(line.split()[3:])
            elif re.match('^[0-9]+', line):  # id
                word = line.split('\t')[1]
                words.append(line.split('\t')[1])
                lemmata.append(line.split('\t')[2])
            elif line == '\n':  # Process text
                print('# source =', source)
                print("# text =", original_text)
                print('{:<25}{:<25}{:<25}{:<25}'.format('word', 'predicted', 'gold', 'correct'))
                print('-' * 107)

                # Get lemmata
                words_doc = lemmatize(" ".join(words))
                for sent in words_doc.sentences:
                    for i, word in enumerate(sent.words):
                        text, predicted, gold = word.text, word.lemma, lemmata[i]

                        # Evaluate
                        if gold != "_":
                            if predicted == gold:
                                verdict = "v"
                                if source.endswith('.xml'):
                                    corr_in_file += 1
                                    corr_total += 1
                            else:
                                verdict = "x"
                                if source.endswith('.xml'):
                                    incorr_in_file += 1
                                    incorr_total += 1
                        else:
                            verdict = ""
                        print('{:<25}{:<25}{:<25}{:<25}'.format(text, predicted, gold, verdict))
                print()
                if source.endswith('.xml'):
                    file_scores[source] = {'score': round(corr_in_file / (corr_in_file + incorr_in_file) * 100, 2),
                                           'correct': corr_in_file, 'incorrect': incorr_in_file}

        print("Score summary by CGRN file:")
        file_scores = sorted(file_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        print('{:<50}{:<15}{:<15}{:<15}'.format('source', 'score (%)', 'correct (#)', 'incorrect (#)'))
        print('-' * 93)
        for scores in file_scores:
            print('{:<50}{:<15}{:<15}{:<15}'.format(scores[0], scores[1]['score'],
                                                    scores[1]['correct'], scores[1]['incorrect']))
        print('-' * 93)
        print("{} out of {} correct ({}%)".format(corr_total, corr_total + incorr_total,
                                                  round(corr_total / (corr_total + incorr_total) *
                                                        100, 2)))


main()
