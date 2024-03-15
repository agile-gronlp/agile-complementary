# This script creates the train, development and test set from the
# CGRN files to train an Ancient Greek lemmatizer using Stanza.

import re  # For extracting XML data
import glob  # For finding CGRN pathnames
from cltk.alphabet.grc import grc  # For normalizing texts
import sys  # For printing feedback
import config  # For corpus filepaths


def extract_words_lemmas(path):
    """
    Extracts all words from the CGRN XML files, mapping them to their gold lemma form.
    :param path: str of the file path to the CGRN file
    :return: list of tuples where tuple[0] is the word and tuple[1] the lemma
    """

    # Retrieve relevant XML
    with open(path, "r") as f:
        xml = ''.join([line.rstrip() for line in f if re.search('\S', line)])  # Omit lines consisting of spaces
    xml = grc.normalize_grc(xml)
    xml = re.findall("<ab.*</ab>", xml, re.DOTALL)  # Cut down to paragraphs
    # Clean XML
    xml = ''.join(xml).replace("\n", "")  # Remove newlines
    xml = re.sub('\s+', ' ', xml)  # Reduce consecutive whitespace
    xml = re.sub('<ab.*?>.*?<', '<', xml).replace('</ab>', '')  # Remove paragraph info
    xml = re.sub('<surplus.*?>.*?</surplus>', '', xml)  # Remove surplus elements
    xml = re.sub('<sic.*?>.*?</sic>', '', xml)  # Remove sic elements
    xml = re.sub('[()?]', '', xml)  # Remove notes
    xml = re.sub('[()]*', '', xml)  # Remove only brackets (e.g. οὕτω(ς) -> οὕτως)
    xml = re.sub('[|∣·∙∶:,.⁝⋮⁞⁙“”]', '', xml)  # Remove extra-alphabetical chars
    # Add custom rules (chars have been normalized)
    xml = re.sub('[Ϝϝh]', '', xml)
    xml = re.sub('(κς)|(κσ)|(χς)|(χσ)', 'ξ', xml)
    xml = re.sub('(Κς)|(Κσ)|(Χσ)|(Χς)', 'Ξ', xml)
    xml = re.sub('(φς)|(φσ)', 'ψ', xml)
    xml = re.sub('(Φς)|(Φσ)', 'Ψ', xml)
    xml = re.sub(' [|∣·∙∶:,.⁝⋮⁞⁙“”]+', '', xml)

    # Extract text within tags (e.g. <w>) and between tags (e.g. not annotated words)
    within_tag = re.compile('<.*?>').findall(xml)
    between_tag = re.compile('>.*?<').findall(xml)
    # Combine lists in alternating fashion to preserve order
    result = [None]*(len(within_tag)+len(between_tag))  # Create list of correct length
    result[::2] = within_tag  # Insert even indexes
    result[1::2] = between_tag  # Insert uneven indexes

    words_lemmas = []
    word = lemma = ""
    for i, match in enumerate(result):

        # Handle linebreaks
        if re.search('<lb .*/>', match):  # If new line
            if 'break="no"' not in re.search('<lb (.*)/>', match).group(1) and word != "":  # If line break
                word, lemma = add_pair(word, lemma, words_lemmas)  # Word complete
            else:
                word = word.rstrip()  # Word incomplete

        # Handle words
        if lemma:  # If currently processing <w> element
            # Text until </w> forms corresponding word
            if re.search('>(.+)<', match):
                word += re.search('>(.+)<', match).group(1)
            elif re.search('</w>', match):
                word, lemma = add_pair(word, lemma, words_lemmas)
        else:
            if re.search('<w lemma=".*">', match):
                lemma = re.search('<w lemma="(.*)">', match).group(1)
                if lemma == "unclear":
                    lemma = "_"
            elif re.search('>(\s+)<', match):  # > <
                word, lemma = add_pair(word, lemma, words_lemmas)
            elif re.search('>(\S+)<', match):  # >C<
                word += re.search('>(.*)<', match).group(1)
            elif re.search('>(\s+\S+)<', match):  # > C<
                word, lemma = add_pair(word, lemma, words_lemmas)
                word += re.search('>\s+(\S+)<', match).group(1)
            elif re.search('>(\S+\s+)<', match):  # >C <
                word += re.search('>(\S+)\s+<', match).group(1)
                word, lemma = add_pair(word, lemma, words_lemmas)
            elif re.search('>(\s+\S+.*\s)<', match):  # > C C( C) <
                word, lemma = add_pair(word, lemma, words_lemmas)
                for word in re.search('>\s+(\S+.*)\s+<', match).group(1).split():
                    word, lemma = add_pair(word, lemma, words_lemmas)
            elif re.search('>(\S+\s+.*\s)<', match):  # >C C( C) <
                word += re.search('>(\S+)\s+.*\s<', match).group(1)
                word, lemma = add_pair(word, lemma, words_lemmas)
                for word in re.search('>\S+\s+(.*)\s<', match).group(1).split():
                    word, lemma = add_pair(word, lemma, words_lemmas)
            elif re.search('>(\S+\s+.*\S+)<', match):  # >C C( C)<
                word += re.search('>(\S+)\s+.*\S+<', match).group(1)
                word, lemma = add_pair(word, lemma, words_lemmas)
                words = re.search('>\S+\s+(.*\S+)<', match).group(1)
                for i, token in enumerate(words.split()):
                    if i < (len(words.split()) - 1):
                        word, lemma = add_pair(token, lemma, words_lemmas)
                    else:  # Last token
                        word += token
            elif re.search('>(\s+\S+.*\S)<', match):  # > C C( C)<
                word, lemma = add_pair(word, lemma, words_lemmas)
                words = re.search('>\s+(\S+.*\S)<', match).group(1)
                for i, token in enumerate(words.split()):
                    if i < (len(words.split()) - 1):
                        word, lemma = add_pair(token, lemma, words_lemmas)
                    else:  # Last token
                        word += token
            if i == (len(result) - 1):  # Last word
                word, lemma = add_pair(word, lemma, words_lemmas)

    return words_lemmas


def add_pair(word, lemma, words_lemmas):
    """
    Adds word-lemma pairs to a list.
    :param word: word (str) to be added
    :param lemma: lemma (str) to be added
    :param words_lemmas: list of tuples where tuple[0] is the word and tuple[1] the lemma
    :return: 2 empty strings to reset the word and lemma vars
    """

    if word != "" and not re.search('[cdfgjlqrsuvw0-9\[\]{}]', word.lower()):
        # Filter alphabet, unrepresentable numerals and incomplete words
        word = word.replace(" ", "")
        if lemma != "":
            words_lemmas.append((word, lemma.strip()))
        else:
            if len(word) == 1 or word[-1] != "," and word[-1] != ".":
                words_lemmas.append((word, '_'))  # Lemma = '_' if unknown
            else:
                words_lemmas.append((word[:-1], '_'))  # Lemma = '_' if unknown
                words_lemmas.append((word[-1], '_'))  # Add punctuation
    return '', ''


def main():

    train_count = dev_count = test_count = 0
    train_path = current_path = config.destination_train_path
    dev_path = config.destination_dev_path
    test_path = config.destination_test_path

    files = glob.glob("CGRN_xml" + "/*")
    files.sort(key=lambda filename: int(filename.split('_')[-1][:-4]))  # Sort by CGRN id
    for sent_id, file in enumerate(files):
        print("Processing {}".format(file), file=sys.stderr)
        tokens_lemmas = extract_words_lemmas(file)
        word_count = lemma_count = 0
        text = ' '.join([token_lemma[0] for token_lemma in tokens_lemmas])
        with open(current_path, "a") as f:
            f.write("# source = {}\n# text = {}\n# sent_id = {}\n".format(file, text, str(sent_id)))
            for i, token_lemma in enumerate(tokens_lemmas):
                word, lemma = token_lemma[0], token_lemma[1]
                word_count += 1
                f.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".
                        format(str(word_count), word, lemma, '_', '_', '_', str(word_count - 1), '_', '_', '_'))
                if lemma != "_":
                    lemma_count += 1
            f.write('\n')

        # Update split sizes
        if current_path == train_path:
            train_count += lemma_count
        elif current_path == dev_path:
            dev_count += lemma_count
        else:  # current_path == test_path
            test_count += lemma_count

        # Change output file for next iteration
        corpus_size = train_count + dev_count + test_count
        if dev_count / corpus_size <= 0.175:
            current_path = dev_path
        elif test_count / corpus_size <= 0.2175:
            current_path = test_path
        else:  # train_count / corpus_size == 0.61
            current_path = train_path

    print("Printed", train_count, "lemmas to train.", file=sys.stderr)
    print("Printed", dev_count, "lemmas to dev.", file=sys.stderr)
    print("Printed", test_count, "lemmas to test.", file=sys.stderr)


if __name__ == "__main__":
    main()
