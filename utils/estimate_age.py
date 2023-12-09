"""Library for estimating the age of an author based on their lexicon.

Does not use semantics, rather, applies a dictionary-based lexical
approach.

Adapted / inspired from https://github.com/GBJim/age_gender_predictor/tree/master
"""
import csv
import os


def _load_age_lexicon() -> dict[str, float]:
    lexicon: dict[str, float] = {}

    # Get the directory of this file.
    # (allows the pathing to work when called from different directories!)
    with open(os.path.dirname(__file__) + "\\emnlp14age.csv", "r") as infile:
        for row in csv.DictReader(infile):
            lexicon[row["term"]] = float(row["weight"])
    return lexicon

_AGE_LEXICON   = _load_age_lexicon()
_AGE_INTERCEPT = _AGE_LEXICON.pop("_intercept")

def estimate_author_age(text: str) -> float:
    """Predict the author's age."""
    
    # Count of all words that are in both the text and the lexicon.
    # Counts each instance of a word seperately.
    match_count = 0
    age         = _AGE_INTERCEPT

    for word in text.split():
        if (word_age := _AGE_LEXICON.get(word)):
            age += word_age
            match_count += 1

    if match_count > 0:
        # Avoid div by zeroes.
        age /= match_count
    return age


if __name__ == "__main__":
    # Test
    urban_dictionary_snippet = """
        Usually used in a negative connotation,
        a "Texaboo" is an individual who is overly obsessed with,
        and loves everything to do with, Texas and goes out of their way
        to pass themselves of as Texans but is not a Texan in any way,
        shape, or form. A Texaboo could be considered the Texas
        equivalent of a Weaboo, but should not be confused with an "Honorary Texan",
        which is somebody who is not a native Texan, but has specific strong ties to
        Texas such as family roots lying in either the State of Texas or Republic of Texas.
    """
    print(estimate_author_age(urban_dictionary_snippet))
