# Reproducing AGILe
This repository complements the [AGILe repository](https://github.com/agile-gronlp/agile) as it was used for training AGILe with Stanza and for evaluating it subsequently. It requires Python 3.7 or above.

## Method
The following steps have been taken to produce the model specifically trained for Ancient Greek inscriptions. 

### 1. Install CLTK
To normalize texts. To install, simply run:  
```
pip install cltk==1.0.16
```  
[Alternative instructions](https://github.com/cltk/cltk#installation "More instructions") are available.

### 2. Clone this repository
```
git clone https://github.com/agile-gronlp/agile-complementary
```

### 3. Download and install Stanza from source
Download and install Stanza from its source repository as follows:
```
cd agile-complementary
wget https://github.com/stanfordnlp/stanza/archive/0a61b80d44d2868a7044ad389917287fea754614.zip
unzip 0a61b80d44d2868a7044ad389917287fea754614.zip
mv stanza-0a61b80d44d2868a7044ad389917287fea754614 stanza 
rm 0a61b80d44d2868a7044ad389917287fea754614.zip
cd stanza
pip install -e .
```

### 4. Download Stanza models
To download the Ancient Greek models from Stanza, follow these steps in your Python interactive interpreter:

```
>>> import stanza
>>> stanza.download('grc')
```

### 5. Make a train, dev and test set
To improve performance on Ancient Greek inscriptions, the [CGRN corpus](http://cgrn.ulg.ac.be/) (Carbon et al., 2016) is used. To improve general performance, the [PROIEL corpus](https://github.com/UniversalDependencies/UD_Ancient_Greek-PROIEL/tree/291e7e16a861e6ec43dd6f167a5f7051677f450c) (Haug and Jøhndal, 2008) is used. [`split_CGRN.py`](https://github.com/agile-gronlp/agile-complementary/blob/master/prepare/split_CGRN.py) separates and preprocesses the [CGRN XML files](https://github.com/agile-gronlp/agile-complementary/tree/master/prepare/CGRN_xml) into 3 representative splits with texts from different periods. [`copy_PROIEL.py`](https://github.com/agile-gronlp/agile-complementary/blob/master/prepare/copy_PROIEL.py) adds the PROIEL splits. The lemmatizer requires CoNLL-U formatted data before training.

To build the different splits, execute the following commands from inside the `agile-complementary/stanza` directory.
```
mkdir -p stanza/utils/datasets/extern_data/ud2/ud-treebanks-v2.7/UD_Ancient_Greek-agile
cd ../prepare
python3 split_CGRN.py  
python3 copy_PROIEL.py
```

Preserving a 60-20-20 split for the CGRN corpus, the composition of the different splits is as follows:
|           | CGRN lemmas | PROIEL lemmas | 
| --------- | ----------- | ------------- | 
| __Train__ | 14,963      | 187,033       | 
| __Dev__   | 5,170       | 13,652        | 
| __Test__  | 5,030       | 13,314        |

### 6. Prepare data for training
Now, convert the data to the format used by the model at training time by executing the following code from inside the `agile-complementary/prepare` directory.

```
cd ../stanza/stanza/utils/datasets
python3 prepare_lemma_treebank.py UD_Ancient_Greek-agile
```

Move the data to the train directory:

```
mv data/ ../training
```

### 7. Train model

The model is ready to be created. 

```
cd ../training
python3 run_lemma.py UD_Ancient_Greek-agile --num_epoch 50 --no_pos --save_dir ../../../../evaluate 
```

### 8. Evaluate

```
cd ../../../../evaluate
python3 evaluate.py
```

As [`evaluate.py`](https://github.com/agile-gronlp/agile-complementary/blob/master/evaluate/agile.py) computes, the system gets __85.09%__ of the CGRN test lemmata correct. Please note this includes custom rules and a lexicon look-up as implemented in [`agile.py`](https://github.com/agile-gronlp/agile-complementary/blob/master/evaluate/agile.py). In addition, the score does not include all articles, particles, conjunctions and prepositions. Furthermore, pretokenized texts are given to the lemmatizer. The custom rules (e.g. the digamma removal) have already been applied at step 5 and thus the evaluation does not show these characters, which is independent from the performance.

## Bibliography
Carbon, J.-M., Peels, S. and V. Pirenne-Delforge. _A Collection of Greek Ritual Norms (CGRN)_, Liège 2016- (http://cgrn.ulg.ac.be, consulted in 2021).

Dag T. T. Haug and Marius L. Jøhndal. 2008. 'Creating a Parallel Treebank of the Old Indo-European Bible Translations'. In Caroline Sporleder and Kiril Ribarov (eds.). _Proceedings of the Second Workshop on Language Technology for Cultural Heritage Data (LaTeCH 2008)_ (2008), pp. 27-34.

de Graaf, E., Stopponi, S., Bos, J., Peels-Matthey, S., & Nissim, M. (2022, June). AGILe: The first lemmatizer for Ancient Greek inscriptions. In The 13th Conference on Language Resources and Evaluation. European Language Resources Association (ELRA),  pp. 5334-5344. https://aclanthology.org/2022.lrec-1.571/

## License
<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.
