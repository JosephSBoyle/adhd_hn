from collections import Counter
import re

import pandas as pd

colnames = ("username", "comment")
adhd = pd.read_csv("adhd_comments.csv", names=colnames)
ctrl = pd.read_csv("ctrl_comments.csv", names=colnames)

adhd.dropna(inplace=True)
ctrl.dropna(inplace=True)

import matplotlib.pyplot as plt

def get_top_k_words(df: pd.DataFrame, k: int):
    word_counter = Counter()

    all_comments = ""
    # Loop through each row and update the counter
    for comment in df["comment"]:
        cleaned_comment = re.sub(r'[^a-zA-Z\s]', '', comment).lower()  # Ignore non-alpha chars and convert to lowercase
        words = cleaned_comment.split()  # Split the string into words
        
        word_counter.update(words)  # Update the counter

        all_comments += cleaned_comment

    from wordcloud import WordCloud

    wordcloud = WordCloud().generate(all_comments)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()
    return Counter(dict(word_counter.most_common(k)))

adhd_top10 = get_top_k_words(adhd, 100)
ctrl_top10 = get_top_k_words(ctrl, 100)
print(adhd_top10)
print(ctrl_top10)
