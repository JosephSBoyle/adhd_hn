"""Library for estimating the gender of an author based on their lexicon.

Does not use semantics, rather, applies a dictionary-based lexical
approach.

Adapted / inspired from https://github.com/GBJim/age_gender_predictor/tree/master
"""
import csv
import os


def _load_gender_lexicon() -> dict[str, float]:
    lexicon: dict[str, float] = {}
    
    # Get the directory of this file.
    # (allows the pathing to work when called from different directories!)
    with open(os.path.dirname(__file__) + "\\emnlp14gender.csv", "r") as infile:
        for row in csv.DictReader(infile):
            lexicon[row["term"]] = float(row["weight"])
    return lexicon

_GENDER_LEXICON   = _load_gender_lexicon()
_GENDER_INTERCEPT = _GENDER_LEXICON.pop("_intercept")

def estimate_author_is_female(text: str) -> float:
    """Predict whether the given text was authored by a female, giving a real-value based on their writing.
    Values less than zero suggest a female author.
    """
    # Count of all words that are in both the text and the lexicon.
    # Counts each instance of a word seperately.
    match_count  = 0
    female_score = _GENDER_INTERCEPT

    for word in text.split():
        if (word_gender := _GENDER_LEXICON.get(word)):
            female_score += word_gender
            match_count += 1

    if match_count > 0:
        # Avoid div by zeroes.
        female_score /= match_count
    return female_score


if __name__ == "__main__":
    ### Test ###
    pride_and_prejudice_snippet = """
        However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families that he is considered as the rightful property of some one or other of their daughters.
        "My dear Mr. Bennet," said his lady to him one day, "have you heard that Netherfield Park is let at last?"
        Mr. Bennet replied that he had not.
        "But it is," returned she; "for Mrs. Long has just been here, and she told me all about it."
        Mr. Bennet made no answer.
        "Do not you want to know who has taken it?" cried his wife impatiently.
        "You want to tell me, and I have no objection to hearing it."
        This was invitation enough.
        "Why, my dear, you must know, Mrs. Long says that Netherfield is taken by a young man of large fortune from the north of England; that he came down on Monday in a chaise and four to see the place, and was so much delighted with it, that he agreed with Mr. Morris immediately; that he is to take possession before Michaelmas, and some of his servants are to be in the house by the end of next week."
        "What is his name?"
        "Bingley."
        "Is he married or single?"
        "Oh! single, my dear, to be sure! A single man of large fortune; four or five thousand a year. What a fine thing for our girls!"
    """
    print(estimate_author_is_female(pride_and_prejudice_snippet))
