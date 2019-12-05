from flask import Flask, request, jsonify
from flask import request
import nltk
import string
import os

app = Flask(__name__)

NOUNTAGS = set(['PRP', 'NNP', 'NN', 'NNPS', 'NNS', 'NOUN'])
LUAN = os.environ.get('LUAN', ':luan:')

@app.route('/luanize', methods=['POST'])
def luanize():
    dataIn = request.form['text']
    luanized = luanizeTextBlock(dataIn)
    return jsonify(text=luanized, response_type="in_channel")

def luanizeTextBlock(rawInput):
    tokd = nltk.word_tokenize(rawInput.strip())
    nouns = {noun[0] for noun in nltk.pos_tag(tokd, tagset="universal") if tagIsNoun(noun)}

    def chunkIsNoun(chunk):
        return chunk.strip(string.punctuation) in nouns

    spaceDelimitedLines = [line.split() for line in rawInput.splitlines()]
    result = ""
    for line in spaceDelimitedLines:
        luanizedWords = [luanizeWord(word) if chunkIsNoun(word)
                         else word
                         for word in line]

        result += " ".join(luanizedWords) + "\n"

    return result

def tagIsNoun(taggedWord):
    return taggedWord[1] in NOUNTAGS

def luanizeWord(word):
    wnl = nltk.stem.WordNetLemmatizer()
    lemma = wnl.lemmatize(word.strip(string.punctuation))
    return word.replace(lemma, LUAN)


ozy = """I MET a Traveler from an antique land,
Who said, "Two vast and trunkless legs of stone
Stand in the desert. Near them, on the sand,
Half sunk, a shattered visage lies, whose frown,
And wrinkled lip, and sneer of cold command,
Tell that its sculptor well those passions read,
Which yet survive, stamped on these lifeless things,
The hand that mocked them and the heart that fed:
And on the pedestal these words appear:
"My name is OZYMANDIAS, King of Kings."
Look on my works ye Mighty, and despair
No thing beside remains. Round the decay
Of that Colossal Wreck, boundless and bare,
The lone and level sands stretch far away."""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')))
