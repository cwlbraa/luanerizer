import nltk

ozy = """I MET a Traveler from an antique land,
Who said, "Two vast and trunkless legs of stone
Stand in the desart. Near them, on the sand,
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

def scratch():
    tokd = nltk.word_tokenize(ozy)
    # print(nltk.pos_tag(tokd))
    taggedWords = nltk.pos_tag(tokd)
    luanizedWords = [luanizeNounLemma(taggedWord) for taggedWord in taggedWords]
    # print(luanizedWords)
    print(" ".join(luanizedWords))


NOUNTAGS = set(['PRP', 'NNP', 'NN', 'NNPS', 'NNS'])
def luanizeNounLemma(taggedWord):
    if taggedWord[1] in NOUNTAGS:
        return luanize(taggedWord[0])
    return taggedWord[0]

def luanize(word):
    wnl = nltk.stem.WordNetLemmatizer()
    lemma = wnl.lemmatize(word)
    return word.replace(lemma, ':luan:')




