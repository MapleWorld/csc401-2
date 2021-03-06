"""
Take tagged and tokenized tweets and build
arff file from them containing 20 required features.
NOTE: I have added -L,-B,-S flags at the beginning, this
indicates that the data should be log transformed (i.e
each feature x becomes ln(x+1)), binarized, or standardized
respectively. These flags are mutually exclusive, and using
more than one of these flags will break the program.
"""

import os
import sys

import numpy as np

__author__ = 'Tal Friedman (talf301@gmail.com)'

def binarize(features):
    """
    Make each feature 1 iff non-zero
    """
    binary = np.asarray([int(x > 0) for x in features])
    return binary
    
def log_trans(features):
    """
    Transform each feature for each data point by log(x+1)
    """
    features = np.array(features)
    features = np.log(features+1)
    return features

def standardize(features):
    """
    Standardize to mean 0, variance 1
    """
    data = np.array(features)
    mean = np.mean(data)
    sd = np.sqrt(np.var(data) + 1e-20)
    data -= mean
    data /= sd
    return data

def count_sat(tweet, f):
    """
    Generic method which counts how many token/tag
    pairs satisfies the two-place function f.
    """
    count = 0
    for line in tweet:
        for token, tag in line:
            if f(token, tag):
                count += 1
    return count

def count_char(tweet, charlist):
    """
    Generic method which counts how many instances of
    a specific character list occur in a tweet.
    """
    count = 0
    for line in tweet:
        for token, _ in line:
            for char in token:
                if char in charlist:
                    count += 1
    return count

def count_token_tag(tweet, wordlist, taglist):
    """
    Generic method for computing features 
    which involve a count of the number of 
    tokens/tag pairs both in correspondoning lists.
    """
    return count_sat(tweet, lambda x,y: x.lower() in wordlist and y in taglist)

def count_token(tweet, wordlist):
    """
    Generic method for computing features
    which inolve a count of the number of tokens
    (not tags) in some list.
    Assumption is that tweets come as a list (entire tweet)
    of lists (sentences) of pairs (token,tag)
    """
    return count_sat(tweet, lambda x,y: x.lower() in wordlist)
    
def count_tag(tweet, taglist):
    """
    Generic method for computing features
    which inolve a count of the number of tags
    in some list.
    Assumption is that tweets come as a list (entire tweet)
    of lists (sentences) of pairs (token,tag)
    """
    return count_sat(tweet, lambda x,y: y in taglist)
    
def av_sen_len(tweet):
    """
    Returns the average length of the sentneces in tokens.
    """
    if len(tweet) == 0: return 0
    return sum(len(l) for l in tweet) / float(len(tweet))

def av_token_len(tweet):
    """
    Returns the average length of tokens excluding punctuation
    """
    total_sum = 0
    total_count = 0
    punc = ['#', '$', '.', ',', ':', '(', ')', '"', "'"]
    for line in tweet:
        for token, tag in line:
            if tag not in punc:
                total_sum += len(token)
                total_count += 1
    if total_count == 0:
        return 0
    return total_sum / float(total_count)

def num_sen(tweet):
    """
    Returns the number of sentences in the given tweet.
    """
    return len(tweet)

def load_wordlist(filename):
    """
    Load a list of words, one per line, from a given
    filename.
    """
    with open(filename, 'rU') as file:
            wordlist = [line.strip().lower() for line in file]
    return wordlist

def count_future_tense(tweet):
    """
    Count the number of instances of future tense verbs
    in a tweet, as described by the forms:
    "'ll", "will", "gonna", or triples in the form 
    "going" "to" "_/VB"
    """
    # First count the simple cases
    count = count_token(tweet, ["'ll", 'will', 'gonna'])
    # Count the triples
    for line in tweet:
        if len(line) < 3: continue
        for i in range(len(line)-2):
            # Hard coded because making this modular seems
            # like an unnecessary amount of work
            if line[i][0] == 'going' and line[i+1][0] == 'to' \
                    and line[i+2][1] == 'VB':
                count += 1
    return count         

def build_line(tweet, class_label, fp_list, sp_list, tp_list, slang_list, do_log, do_stand, do_bin):
    """
    Takes a tweet in our processed format along with a 
    class label and whatever wordlists we need, and returns
    the line to be written to arff file.
    """
    features = []
    # First person pronouns
    features.append(count_token_tag(tweet, fp_list, ['PRP', 'PRP$']))
    # Second perosn pronouns
    features.append(count_token_tag(tweet, sp_list, ['PRP', 'PRP$']))
    # Third person pronouns
    features.append(count_token_tag(tweet, tp_list, ['PRP', 'PRP$']))
    # Coordinating conjunctions
    features.append(count_tag(tweet, ['CC']))
    # Past tense verbs
    features.append(count_tag(tweet, ['VBD']))
    # Future tense verbs
    features.append(count_future_tense(tweet))
    # Commas
    features.append(count_tag(tweet, [',']))
    # Colons/semicolons
    features.append(count_token(tweet, [';', ':']))
    # Dashes
    features.append(count_char(tweet, ['-']))
    # Parentheses
    features.append(count_tag(tweet, ['(', ')']))
    # Ellipses
    features.append(count_token(tweet, ['...']))
    # Common nouns
    features.append(count_tag(tweet, ['NN', 'NNS']))
    # Proper nouns
    features.append(count_tag(tweet, ['NNP', 'NNPS']))
    # Adverbs
    features.append(count_tag(tweet, ['RB', 'RBR', 'RBS']))
    # wh-words
    features.append(count_tag(tweet, ['WDT', 'WP', 'WP$', 'WRB']))
    # Slang
    features.append(count_token(tweet, slang_list))
    # All upper
    features.append(count_sat(tweet, lambda x,y: len(x) > 1 and x.isupper()))
    # Average sentence length
    features.append(av_sen_len(tweet))
    # Average token length
    features.append(av_token_len(tweet))
    # Number of sentences
    features.append(num_sen(tweet))

    # If necessary, log transform features
    if do_log:
        features = log_trans(features)
    # If necessary, standardize
    if do_stand:
        features = standardize(features)
    # If necessary, binarize
    if do_bin:
        features = binarize(features)
    # To strings
    features = [str(f) for f in features]

    # EXTRA FEATURES HERE
    
    # Class label
    features.append(class_label)
    return ','.join(features)+'\n'

def main(args=sys.argv[1:]):
    # Get if we need to standardize features before spitting them out
    do_stand = False
    if args[0] == '-S':
        do_stand = True
        args = args[1:]
    # Get if we need to binarize features before spitting them out
    do_bin = False
    if args[0] == '-B':
        do_bin = True
        args = args[1:]
    # Get if we need to log transform features before spitting them out
    do_log = False
    if args[0] == '-L':
        do_log = True
        args = args[1:]

    # Get if we need to use the first X tweets
    num_tweets = 0
    if args[0].startswith('-'):
        num_tweets = int(args[0][1:])
        args = args[1:]
    classes = []

    # Load in required wordlists
    fp_list = load_wordlist('/u/cs401/Wordlists/First-person')
    sp_list = load_wordlist('/u/cs401/Wordlists/Second-person')
    tp_list = load_wordlist('/u/cs401/Wordlists/Third-person')
    slang_list = load_wordlist('/u/cs401/Wordlists/Slang')
    # Compile a list of lists for classes, first entry is name,
    # the rest are file names to draw from
    for raw_class in args[:-1]:
        split_class = raw_class.split(':')
        if len(split_class) == 1:
            files = raw_class.split('+')
            class_name = ''
            for file in files:
                class_name += file.split('.')[0]
            classes.append([class_name] + files)
        else:
            classes.append([split_class[0]] + split_class[1].split('+'))

    # Create output file and write all the headers
    out_filename = args[-1]
    out_file = open(out_filename, 'w')
    out_file.write('@relation %s\n\n' % out_filename.split('.')[0])
    # To add another numeric feature to header, just add to this list
    numer_features = ['fpp_count', 'spp_count', 'tpp_count', 'cc_count', 'ptv_count',
            'ftv_count', 'comma_count', '(semi)colon_count', 'dash_count', 'paren_count',
            'ellipse_count', 'cn_count', 'pn_count', 'adv_count', 'wh_count', 'slang_count',
            'allcaps_count', 'sen_len', 'token_len', 'num_sen']
    for feature in numer_features:
        out_file.write('@attribute %s numeric\n' % feature)
    out_file.write('@attribute class {%s}\n\n' % ', '.join([l[0] for l in classes]))
    out_file.write('@data\n')
    
    # Create actual data lines
    for c in classes:
        for filename in c[1:]:
            file = open(filename, 'rU')
            curr_tweet = []
            count = 0
            for line in file:
                if line.strip() == '|':
                    to_write = build_line(curr_tweet, c[0], fp_list, sp_list, tp_list, slang_list, do_log, do_stand, do_bin)
                    out_file.write(to_write)
                    curr_tweet = []
                    # Update/check count
                    count += 1
                    if num_tweets > 0 and count >= num_tweets:
                        break
                else:
                    pairs = line.strip().split()
                    # Only take the first 2 in case of something weird going on in parsing (e.g. uncaught URL)
                    curr_tweet.append([p.split('/')[:2] for p in pairs])


if __name__ == '__main__':
    sys.exit(main())
