import os
import random
import textwrap
import feedparser


#---- borrowed from ------------------------------------------------
import sys

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
#---- end borrow ---------------------------------------------------


#---- borrowed from ------------------------------------------------
# https://stackoverflow.com/a/7778368
from HTMLParser import HTMLParser
import htmlentitydefs
class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.result = [ ]
    def handle_data(self, d):
        self.result.append(d)
    def handle_charref(self, number):
        codepoint = int(number[1:], 16) if number[0] in (u'x', u'X') else int(number)
        self.result.append(unichr(codepoint))
    def handle_entityref(self, name):
        codepoint = htmlentitydefs.name2codepoint[name]
        self.result.append(unichr(codepoint))
    def get_text(self):
        return u''.join(self.result)

def html_to_text(html):
    s = HTMLTextExtractor()
    s.feed(html)
    return s.get_text()
#---- end borrow ---------------------------------------------------


#----------------------------------------------------------------------
# Input:  blob of text.
# Output: list of lines at most `linelength` long
def break_into_bits(text, linelength):
    return textwrap.wrap(text, linelength)

# Returns a brand new array. Does not alter the input.
def shuffle(array):
    return random.sample(array, len(array))

# Returns a single string text blog of NYT daily article summaries.
def fetch_nytSummaries():
    url = "http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
    feed = feedparser.parse(url)
    summaries = [x.summary for x in feed.entries if len(x.summary)]
    return html_to_text(' '.join(summaries)).strip()

# Returns a single string containing the summary of today's featured article.
def fetch_wikipediaFeaturedArticle():
    url = "https://en.wikipedia.org/w/api.php?action=featuredfeed" \
        + "&feed=featured&feedformat=atom"
    feed = feedparser.parse(url)
    summary = html_to_text(feed.entries[0].summary)
    summary_minus_crap = summary.split("(Full")[0].strip()
    return summary_minus_crap

def fetch_arxivSummary():
    topics = [
        'astro-ph', 'cond-mat', 'cs', 'econ', 'eess', 'gr-qc', 'hep-ex',
        'hep-lat', 'hep-ph', 'hep-th', 'math', 'math-ph', 'nlin', 'nucl-ex',
        'nucl-th', 'physics', 'q-bio', 'q-fin', 'quant-ph', 'stat'
        ]
    topic = random.sample(topics, 1)[0]
    url = 'http://export.arxiv.org/rss/' + topic
    feed = feedparser.parse(url)
    summary = html_to_text(feed.entries[0].summary).strip()
    return summary

def fetch_cocktailRecipes():
    url = 'http://www.drinknation.com/rss/newest'
    feed = feedparser.parse(url)
    summaries = [x.summary for x in feed.entries if len(x.summary)]
    return html_to_text(' '.join(summaries)).strip()

def fetch_onionSummaries():
    url = "http://www.theonion.com/rss"
    feed = feedparser.parse(url)
    summaries = [x.summary for x in feed.entries if len(x.summary)]
    cleaned = [html_to_text(x.split("Read more...")[0].strip()) for x in summaries]
    return (' '.join(cleaned)).strip()

# Posts a tweet, properly encoded and all.
def tweet_it(text):
    # The JSON library serializes text, escaping single quotes.
    os.system("twurl -d 'status=" \
            + text.replace("'", "\\'").encode('utf-8') \
            + "' /1.1/statuses/update.json > twurl.log")
#----------------------------------------------------------------------



# How many chars long should chopped pieces be?
linelength  = 40
tweetlength = 140

print('Fetching text sources...')

# A list of all text blobs to be used in shuffling.
list_of_texts = [
    fetch_nytSummaries(),
    fetch_wikipediaFeaturedArticle(),
    fetch_arxivSummary(),
    fetch_cocktailRecipes(),
    fetch_onionSummaries()
    ]

print('Done. Processing text...')

# All the text lines we're working with.
all_text = ' '.join(list_of_texts)

# We'll loop through until we get a satisfactory one.
posted = False
while not posted:
    # Clip off a few words from the front (amounts to
    # a 'phase shift' of the lines.)
    clipped_text = all_text.split(' ', random.randint(0,30))[-1]
    lines = break_into_bits(clipped_text, linelength)

    # Shuffle them (creates new array).
    shuffled_lines = shuffle(lines)

    # Stitch them together, wrap them again at 140 chars, and take the first line.
    blob = ' '.join(shuffled_lines)

    # As a test: make every tweet begin at the beginning of a sentence.
    blob2 = blob[(blob.find('.')+1):].strip()

    # Break it up and take the first.
    tweets = break_into_bits(blob2, tweetlength)
    tweet = tweets[0].strip()

    # Now tweet it.
    print("The tweet is:\n")
    print(tweet)
    posted = query_yes_no("\nPost it?")

tweet_it(tweet)

print("Done :)")
