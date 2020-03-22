'''
CLASS: Natural Language Processing

Adapted from: https://github.com/charlieg/A-Smattering-of-NLP-in-Python

What is NLP?
- Using computers to process (analyze, understand, generate) natural human languages

Why NLP?
- Most knowledge created by humans is unstructured text
- Need some way to make sense of it
- Enables quantitative analysis of text data

Why NLTK?
- High-quality, reusable NLP functionality
'''

import nltk
nltk.download()


'''
Tokenization

What:  Separate text into units such as sentences or words
Why:   Gives structure to previously unstructured text
Notes: Relatively easy with English language text, not easy with some languages
'''

# "corpus" = collection of documents
# "corpora" = plural form of corpus
from nltk.corpus import webtext
webtext.fileids()

# wine reviews corpus
text = webtext.raw('wine.txt')
text[:500]

# tokenize into sentences
sentences = [sent for sent in nltk.sent_tokenize(text)]
sentences[:10]

# tokenize into words
tokens = [word for word in nltk.word_tokenize(text)]
tokens[:100]

# only keep tokens that start with a letter (using regular expressions)
import re
clean_tokens = [token for token in tokens if re.search(r'^[a-zA-Z]+', token)]
clean_tokens[:100]

# count the tokens
from collections import Counter
c = Counter(clean_tokens)
c.most_common(25)       # mixed case
sorted(c.items())[:25]  # counts similar words separately
for item in sorted(c.items())[:25]:
    print item[0], item[1]


'''
Stemming
What:  Reduce a word to its base/stem/root form
Why:   Often makes sense to treat multiple word forms the same way
Notes: Uses a "simple" and fast rule-based approach
       Output can be undesirable for irregular words
       Stemmed words are usually not shown to users (used for analysis/indexing)
       Some search engines treat words with the same stem as synonyms
'''

from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer('english')

# example stemming
stemmer.stem('charge')
stemmer.stem('charging')
stemmer.stem('charged')

# stem the tokens
stemmed_tokens = [stemmer.stem(t) for t in clean_tokens]

# count the stemmed tokens
c = Counter(stemmed_tokens)
c.most_common(25)       # all lowercase
sorted(c.items())[:25]  # some are strange


'''
Lemmatization
What:  Derive the canonical form ('lemma') of a word
Why:   Can be better than stemming
Notes: Uses a dictionary-based approach (slower than stemming)
'''

lemmatizer = nltk.WordNetLemmatizer()

# compare stemmer to lemmatizer
temp_sent = 'Several women told me I have lying eyes'
[stemmer.stem(t) for t in nltk.word_tokenize(temp_sent)]
[lemmatizer.lemmatize(t) for t in nltk.word_tokenize(temp_sent)]


'''
Stopword Removal
What:  Remove common words that will likely appear in any text
Why:   They don't tell you much about your text
'''

# most of top 25 stemmed tokens are "worthless"
c.most_common(25)

# view the list of stopwords
stopwords = nltk.corpus.stopwords.words('english')
sorted(stopwords)

# stem the stopwords
stemmed_stops = [stemmer.stem(t) for t in stopwords]

# remove stopwords from stemmed tokens
stemmed_tokens_no_stop = [stemmer.stem(t) for t in stemmed_tokens if t not in stemmed_stops]
c = Counter(stemmed_tokens_no_stop)
c.most_common(25)


'''
Named Entity Recognition
What:  Automatically extract the names of people, places, organizations, etc.
Why:   Can help you to identify "important" words
Notes: Training NER classifier requires a lot of annotated training data
       Should be trained on data relevant to your task
       Stanford NER classifier is the "gold standard"
'''

def extract_entities(text):
    entities = []
    # tokenize into sentences
    for sentence in nltk.sent_tokenize(text):
        # tokenize sentences into words
        # add part-of-speech tags
        # use NLTK's NER classifier
        chunks = nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sentence)))
        # parse the results
        entities.extend([chunk for chunk in chunks if hasattr(chunk, 'label')])
    return entities

for entity in extract_entities('Kevin and Josiah are instructors for General Assembly in Washington, D.C.'):
    print '[' + entity.label() + '] ' + ' '.join(c[0] for c in entity.leaves())


'''
Term Frequency - Inverse Document Frequency (TF-IDF)
What:  Computes "relative frequency" that a word appears in a document
           compared to its frequency across all documents
Why:   More useful than "term frequency" for identifying "important" words in
           each document (high frequency in that document, low frequency in
           other documents)
Notes: Used for search engine scoring, text summarization, document clustering
'''

sample = ['Bob likes sports', 'Bob hates sports', 'Bob likes likes trees']

from sklearn.feature_extraction.text import CountVectorizer
vect = CountVectorizer()
vect.fit_transform(sample).toarray()
vect.get_feature_names()

from sklearn.feature_extraction.text import TfidfVectorizer
tfidf = TfidfVectorizer()
tfidf.fit_transform(sample).toarray()
tfidf.get_feature_names()


'''
EXAMPLE: Automatically summarize a document
'''

# corpus of 2000 movie reviews
from nltk.corpus import movie_reviews
reviews = [movie_reviews.raw(filename) for filename in movie_reviews.fileids()]

# create document-term matrix
tfidf = TfidfVectorizer(stop_words='english')
dtm = tfidf.fit_transform(reviews)
features = tfidf.get_feature_names()

import numpy as np

# find the most and least "interesting" sentences in a randomly selected review
def summarize():
    
    # choose a random movie review    
    review_id = np.random.randint(0, len(reviews))
    review_text = reviews[review_id]

    # we are going to score each sentence in the review for "interesting-ness"
    sent_scores = []
    # tokenize document into sentences
    for sentence in nltk.sent_tokenize(review_text):
        # exclude short sentences
        if len(sentence) > 6:
            score = 0
            token_count = 0
            # tokenize sentence into words
            tokens = nltk.word_tokenize(sentence)
            # compute sentence "score" by summing TFIDF for each word
            for token in tokens:
                if token in features:
                    score += dtm[review_id, features.index(token)]
                    token_count += 1
            # divide score by number of tokens
            sent_scores.append((score / float(token_count + 1), sentence))

    # lowest scoring sentences
    print '\nLOWEST:\n'
    for sent_score in sorted(sent_scores)[:3]:
        print sent_score[1]

    # highest scoring sentences
    print '\nHIGHEST:\n'
    for sent_score in sorted(sent_scores, reverse=True)[:3]:
        print sent_score[1]

# try it out!
summarize()


'''
TextBlob Demo: "Simplified Text Processing"
Installation: pip install textblob
'''

from textblob import TextBlob, Word

# identify words and noun phrases
blob = TextBlob('Kevin and Josiah are instructors for General Assembly in Washington, D.C.')
blob.words
blob.noun_phrases

# sentiment analysis
blob = TextBlob('I hate this horrible movie. This movie is not very good.')
blob.sentences
blob.sentiment.polarity
[sent.sentiment.polarity for sent in blob.sentences]

# singularize and pluralize
blob = TextBlob('Put away the dishes.')
[word.singularize() for word in blob.words]
[word.pluralize() for word in blob.words]

# spelling correction
blob = TextBlob('15 minuets late')
blob.correct()

# spellcheck
Word('parot').spellcheck()

# definitions
Word('bank').define()
Word('bank').define('v')

# translation and language identification
blob = TextBlob('Welcome to the classroom.')
blob.translate(to='es')
blob = TextBlob('Hola amigos')
blob.detect_language()
