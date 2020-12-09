"""
ye olden luanerizer - a slack slash-command for luanerizing
"""
import string
import os
from flask import Flask, request, jsonify
from cloudevents.http import CloudEvent, to_binary, from_http
import requests

app = Flask(__name__)

NOUNTAGS = set(["PRP", "NNP", "NN", "NNPS", "NNS", "NOUN"])
LUAN = os.environ.get("LUAN", ":luan:")
BROKER_URL = os.environ.get("BROKER_URL", "https://lol.org")


@app.route("/luanize", methods=["POST"])
def luanize_post_sync():
    """
    takes a form-encoded "text" field and returns some json for the slackbot
    """
    return jsonify(response(request.form["text"]))


@app.route("/luanize_async", methods=["POST"])
def luanize_post_async():
    """
    takes a form-encoded "text" field & response_url and enqueues a event to luanerize the text
    """
    attributes = {
        "type": "dev.cwlbraa.luanerizer",
        "source": request.base_url,
    }
    data = {"text": request.form["text"], "response_url": request.form["response_url"]}
    headers, body = to_binary(CloudEvent(attributes, data))
    requests.post(BROKER_URL, data=body, headers=headers)
    return "", 200


@app.route("/", methods=["POST"])
def home():
    """
    route for processing cloud event emitted by post_async
    """
    event = from_http(request.headers, request.get_data())
    requests.post(event.data["response_url"], json=response(event.data["text"]))
    return "", 204


def response(text):
    """
    returns the json dict with, luanerized text to send to slack
    """
    return {"text": luanerize(text), "response_type": "in_channel"}


def luanerize(text):
    """
    takes text, finds the nouns, and turns them into luans
    """
    nouns = set(find_nouns(text))

    def is_noun(chunk):
        return chunk.strip(string.punctuation) in nouns

    def luanerize_if_noun(word):
        return luanerize_word(word) if is_noun(word) else word

    space_delimited_lines = [line.split() for line in text.splitlines()]
    result = ""
    for line in space_delimited_lines:
        luanerized_words = map(luanerize_if_noun, line)
        result += " ".join(luanerized_words) + "\n"

    return result


def find_nouns(text):
    """
    returns an iterator over all the nouns in the text
    """

    import nltk  # pylint: disable=import-outside-toplevel

    tagged = nltk.pos_tag(nltk.word_tokenize(text.strip()), tagset="universal")
    tagged_nouns = filter(tagged_word_is_noun, tagged)
    return map(lambda tagged: tagged[0], tagged_nouns)


def tagged_word_is_noun(word_with_tag):
    """
    returns true when a tagged word has a nouny part-of-speech
    """
    return word_with_tag[1] in NOUNTAGS


def luanerize_word(word):
    """
    replace the lemma (ie the non-modifier part of the word)
    with luan
    """

    import nltk  # pylint: disable=import-outside-toplevel

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
