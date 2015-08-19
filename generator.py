#!/usr/local/bin/python
import re, sys, random

# Initialize Mapping
tempMapping = {}
mapping = {}
starts = []

# Tuples can be hashed; lists can't. We need hashable values for dict keys.
def toHashKey(lst):
  return tuple(lst)

# Function to fix capitalization of all words.
def fixCaps(word):
  # Ex: "FOO" => "foo"
  if (word.isupper() and (word != "I")):
    word = word.lower()
  # Keep Proper Nouns Capital
  # Ex: "LaTeX" => "Latex"
  elif word[0].isupper():
    word = word.lower().capitalize()
  # Everything else goes to lowercase
  # Ex: "wOOt" => "woot"
  else:
    word = word.lower()
  return word

# Get contents of file, split into a list of words and (some) punctuation
def wordlist(filename):
  f = open(filename, 'r')
  wordlist = [fixCaps(w) for w in re.findall(r"[\w']+|[.,!?;]", f.read())]
  f.close()
  return wordlist

# Adds "word" to the "tempMapping" dict under "history"
# tempMapping matches each word to a list of possible next words.
# Given history = ["the "rain", "in"] and words = "Spain", we add Spain to
# the entries for ["the", "rain", "in"], ["rain", "in"], and ["in"]
def addItemToTempMapping(history, word):
  global tempMapping
  while len(history) > 0:
    first = toHashKey(history)
    if first in tempMapping:
      if word in tempMapping[first]:
        tempMapping[first][word] += 1.0
      else:
        tempMapping[first][word]  = 1.0
    else:
      tempMapping[first] = {}
      tempMapping[first][word] = 1.0
    history = history[1:]

#Building and normalizing the mapping.
def buildMapping(wordlist, markovLength):
  global tempMapping
  starts.append(wordlist[0])
  for i in xrange(1, len(wordlist)-1):
    if i <= markovLength:
      history = wordlist[:i+1]
    else:
      history = wordlist[i - markovLength + 1 : i + 1]
    follow = wordlist[i + 1]
    # if the last elt was a period, add the next word to the start list
    if history[-1] == "." and follow not in ".,!?;":
      starts.append(follow)
    addItemToTempMapping(history, follow)
  # Normalize the values in tempMapping, put them into mapping
  for first, followset in tempMapping.iteritems():
    total = sum(followset.values())
    # Normalize
    mapping[first] = dict([(k, v / total) for k, v in followset.iteritems()])

# Returns the next word in the sentence (chosen randomly) given the previous ones.
def next(prevList):
  sum = 0.0
  retval = ""
  index = random.random()
  # Shorten prevList until it's in mapping:
  while toHashKey(prevList) not in mapping:
    prevList.pop(0)
  # Get a random word from the mapping, given prevList
  for k, v in mapping[toHashKey(prevList)].iteritems():
    sum += v
    if ((sum >= index) and (retval == "")):
      retval = k
  return retval

def genSentence(markovLength):
  # Start with a random "starting word"
  curr = random.choice(starts)
  sent = curr.capitalize()
  prevList = [curr]

  # Keep adding words until we hit a period
  while (curr not in ".!?"):
    curr = next(prevList)
    prevList.append(curr)
    # if the prevList has gotten too long, trim it
    if (len(prevList) > markovLength):
      prevList.pop(0)
    if (curr not in ".,!?;"):
      sent += " " # Add spaces between words (but not punctuation)
    sent += curr

  if (len(sent.split()) < 3): # If sentence is too short, try again
    return genSentence(markovLength)
  else:
    return sent


def main():
  if (len(sys.argv) < 2):
    sys.stderr.write('Usage: ' + sys.argv[0] + ' text_source [chain_length=1]\n')
    sys.exit(1)

  filename = sys.argv[1]
  markovLength = 1
  genNSentences = 1
  if (len(sys.argv) >= 3):
    markovLength = int(sys.argv[2])
  if (len(sys.argv) >= 4):
    genNSentences = int(sys.argv[3])

  buildMapping(wordlist(filename), markovLength)

  for j in xrange(genNSentences):
    print genSentence(markovLength)
    print "\n\n"

if __name__ == "__main__":
  main()





