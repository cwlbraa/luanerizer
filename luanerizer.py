"""
ye olden luanerizer - a slack slash-command for luanerizing
"""
import string
import os
from flask import Flask, request, jsonify
from cloudevents.http import CloudEvent, to_structured, from_http
import requests
import nltk

app = Flask(__name__)

NOUNTAGS = set(["PRP", "NNP", "NN", "NNPS", "NNS", "NOUN"])
LUAN = os.environ.get("LUAN", ":luan:")
BROKER_URL = os.environ.get("LUAN", ":luan:")

@app.route("/luanize", methods=["POST"])
def luanize_post():
    """
    takes a form-encoded "text" field and returns some json for the slackbot
    """
    return jsonify(text=luanize(request.form["text"]), response_type="in_channel")

@app.route("/", methods=["POST"])
def home():
    event = from_http(request.headers, request.get_data())
    print(
        f"""
        Found {event['id']} from {event['source']} with type "
        {event['type']} and specversion {event['specversion']} "
        text: {event['text']}"
        response_url: {event['response_url']}
        """
    )
    return "", 204

def luanize_post_async(function_request):
    """
    takes a form-encoded "text" field & response_url and enqueues a event to luanize the text
    """
    attributes = {
        "type": "dev.cwlbraa.luanerizer",
        "source": function_request.host_url,
    }
    data = {
        "text": function_request.form["text"],
        "response_url": function_request.form["response_url"]
    }
    event = CloudEvent(attributes, data)

    # Creates the HTTP request representation of the CloudEvent in structured content mode
    headers, body = to_structured(event)
    requests.post(BROKER_URL, data=body, headers=headers)
    return "", 200

def luanize(text):
    """
    takes text, finds the nouns, and turns them into luans
    """
    nouns = find_nouns(text)

    def is_noun(chunk):
        return chunk.strip(string.punctuation) in nouns

    space_delimited_lines = [line.split() for line in text.splitlines()]
    result = ""
    for line in space_delimited_lines:
        luanized_words = [
            luanize_word(word) if is_noun(word) else word for word in line
        ]

        result += " ".join(luanized_words) + "\n"

    return result


def find_nouns(text):
    """
    returns all the nouns in the text
    """
    tagged = nltk.pos_tag(nltk.word_tokenize(text.strip()), tagset="universal")
    tagged_nouns = filter(tagged_word_is_noun, tagged)
    return map(lambda tagged: tagged[0], tagged_nouns)

def tagged_word_is_noun(word_with_tag):
    """
    returns true when a tagged word has a nouny part-of-speech
    """
    return word_with_tag[1] in NOUNTAGS


def luanize_word(word):
    """
    replace the lemma (ie the non-modifier part of the word)
    with luan
    """
    wnl = nltk.stem.WordNetLemmatizer()
    lemma = wnl.lemmatize(word.strip(string.punctuation))
    return word.replace(lemma, LUAN)


OZY = """I MET a Traveler from an antique land,
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
