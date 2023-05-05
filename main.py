import re
from duckduckgo_search import ddg
from jaro import jaro_winkler_metric as distance
import multiprocessing

# Define a regular expression pattern to match sentences
sentence_pattern = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s')

# Define a regular expression pattern to exclude sentences containing digits
not_in_sentence = re.compile(r'\[\d*\]|\d+')

sentences = []

# Open the input file
with open('./text-to-cite.txt', 'r') as f:
    # Read the file contents
    text = f.read()

    # Split the text into sentences using the pattern
    s = sentence_pattern.split(text)

    # Extract the sentences that don't contain digits
    for sentence in s:
        if len(not_in_sentence.findall(sentence.strip())) == 0:
            sentences.append(sentence.strip())

sentences_urls = []


def process_sentence(sentence):
    # Use DuckDuckGo to search for the sentence
    r = ddg('inurl:' + sentence, max_results=100)
    if not r:
        return {'sentence': sentence, 'url': 'original_sentence'}
    # Find the link with the highest Jaro distance score
    max_score = 0.0
    max_link = None
    for link in r:
        score = distance(link['body'], sentence)
        if score > max_score:
            max_score = score
            max_link = link

    # If a link was found, add it to the list of sentence URLs
    if max_link and max_score >= 0.65:
        return {'sentence': sentence, 'url': max_link['href'], 'title': max_link['title']}
    else:
        return {'sentence': sentence, 'url': 'original_sentence'}


if __name__ == '__main__':
    multiprocessing.freeze_support()
    # Use multiprocessing to search the internet for each sentence
    with multiprocessing.Pool(processes=4) as pool:
        sentences_urls = pool.map(process_sentence, sentences)

    # Print out the sentence URLs
    for sentence_url in sentences_urls:
        print(f"{sentence_url['sentence']}: {sentence_url['url']}")
