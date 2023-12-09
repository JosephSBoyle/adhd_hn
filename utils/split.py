import random; random.seed(7777) # seed for repro.
import pandas as pd


def train_test_split(df: pd.DataFrame, train_proportion: float) -> tuple[pd.DataFrame]:
    # Split on usernames, so that one user's comments are not both in train and in test.
    usernames = list(set(df["username"]))
    train_usernames = set(random.sample(usernames,
                                        int(train_proportion * len(usernames))))
    
    train_df = df[df["username"].isin(train_usernames)]
    test_df  = df[~df["username"].isin(train_usernames)]

    assert set(train_df["username"]).intersection(test_df["username"]) == set()
    return train_df, test_df