import os
import random
import textwrap
import feedparser

#---- borrowed from
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
#---- end borrow


#----------------------------------------------------------------------
# Input:  blob of text.
# Output: list of lines at most `linelength` long
def break_into_bits(text, linelength):
    return textwrap.wrap(text, linelength)

# Returns a brand new array. Does not alter the input.
def shuffle(array):
    return random.sample(array, len(array))

# Returns a single string text blog of NYT daily article summaries.
def fetch_nytsummaries():
    url = "http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
    feed = feedparser.parse(url)
    entries = feed['entries']
    summaries = [x.summary for x in feed.entries if len(x.summary)]
    return html_to_text(' '.join(summaries))

# Returns a single string containing the summary of today's featured article.
def fetch_wikipediaFeaturedArticle():
    url = "https://en.wikipedia.org/w/api.php?action=featuredfeed" \
        + "&feed=featured&feedformat=atom"
    feed = feedparser.parse(url)
    summary = html_to_text(feed.entries[0].summary)
    summary_minus_crap = summary.split("(Full")[0].strip()
    return summary_minus_crap

# Posts a tweet, properly encoded and all.
def tweet_it(text):
    # The JSON library serializes text, escaping single quotes.
    os.system("twurl -d 'status=" \
            + text.replace("'", "\\'").encode('utf-8') \
            + "' /1.1/statuses/update.json")
#----------------------------------------------------------------------



# How many chars long should chopped pieces be?
linelength  = 60
tweetlength = 140

print('Fetching text sources...')

# A list of all text blobs to be used in shuffling.
list_of_texts = [
    fetch_nytsummaries(),
    fetch_wikipediaFeaturedArticle()
    ]

print('Done. Processing text...')

# All the text lines we're working with.
all_text = ' '.join(list_of_texts)
# Clip off a few words from the front (amounts to
# a 'phase shift' of the lines.)
clipped_text = all_text.split(' ', random.randint(0,30))[-1]
lines = break_into_bits(clipped_text, linelength)

# Shuffle them (creates new array).
shuffled_lines = shuffle(lines)

# Stitch them together, wrap them again at 140 chars, and take the first line.
blob = ' '.join(shuffled_lines)
tweets = break_into_bits(blob, tweetlength)
tweet = tweets[0].strip()

print('Done. Tweeting...')

# Now tweet it.
print("Tweet is:")
print(tweet)
tweet_it(tweet)

print("\nDone :)")
