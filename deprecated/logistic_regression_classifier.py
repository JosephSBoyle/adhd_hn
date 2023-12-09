import pandas as pd

from split import train_test_split

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import accuracy_score


all_comments = pd.read_csv("comments.csv")
train, test = train_test_split(all_comments, train_proportion=0.5)
# Convert text to TF-IDF features, fit on train.

# vectorizer = TfidfVectorizer(max_features=100_000)
vectorizer = CountVectorizer(max_features=100_000)

transform  = vectorizer.fit(train.comment)

Xtrain = transform.transform(test.comment)
Xtest  = transform.transform(test.comment)

# Train a logistic regression classifier
clf = LogisticRegression()
clf.fit(Xtrain, train.reported_adhd)

# Predict labels for the test set
y_pred_train = clf.predict(Xtrain)
y_pred_test  = clf.predict(Xtest)

# Evaluate the model
print("Test  Accuracy:", accuracy_score(train.reported_adhd, y_pred_train))
print("Train Accuracy:", accuracy_score(test.reported_adhd, y_pred_test))


### Evaluate model on specific username
from hn_api import get_comments_by_user
# username = input("Enter a username: ")
username = "extasia"
comments = get_comments_by_user(username, 500)

import numpy as np
Xuser = transform.transform(comments)
print("Prediction: ", np.mean(clf.predict(Xuser)))


### Word importances
feature_names = vectorizer.get_feature_names_out()
assert len(feature_names) == len(clf.coef_[0])

ordered_indices = np.argsort(clf.coef_)[0]
for idx in ordered_indices:
    print(f"{feature_names[idx]:<15} {clf.coef_[0][idx]:<15}")