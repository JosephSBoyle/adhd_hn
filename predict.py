import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.ensemble import AdaBoostClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (classification_report, confusion_matrix,
                             roc_auc_score, roc_curve)
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

import matplotlib; matplotlib.use('Qt5Agg')

df = pd.read_csv("./data/comments_stratified_balanced.csv")
df = df[["username", "reported_adhd", "comment"]]

X_train, X_test, y_train, y_test  = train_test_split(
    df["comment"],
    df["reported_adhd"],
    train_size=0.90,
    stratify=df["reported_adhd"],
    random_state=7777
)

pipe = Pipeline([
    ('vectorizer', TfidfVectorizer()),
    # ('svc', SVC())
    ('lr',  LogisticRegression(class_weight='balanced'))
])

### Find best hyperparameters
# Define the parameter grid
param_grid = {
    'vectorizer__max_features': (100, 200, 300),
}

grid_search = GridSearchCV(pipe, param_grid, cv=5, scoring='accuracy')
grid_search.fit(X_train, y_train)

# Print the best parameters and the corresponding score
print("Best Parameters: ", grid_search.best_params_)
print("Best Cross-Validation Score: ", grid_search.best_score_)

# Evaluate the best model on the test set
best_model = grid_search.best_estimator_
test_acc   = best_model.score(X_test, y_test)
print("Best model's Test Set Accuracy: ", test_acc)

### See top features: ####
if "lr" in best_model.named_steps:
    feature_names = best_model.named_steps["vectorizer"].get_feature_names_out()
    coefficients  = best_model.named_steps["lr"].coef_[0]

    feature_weights = pd.DataFrame({'Feature': feature_names, 'Weight': coefficients})
    print(feature_weights.sort_values("Weight", ascending=False, key=abs))
##########################


y_test_pred       = best_model.predict(X_test)
y_test_pred_proba = best_model.predict_proba(X_test)

print(classification_report(y_test, y_test_pred))
print(roc_auc_score(y_test, y_test_pred))


# Generate the confusion matrix
cm = confusion_matrix(y_test, y_test_pred)

# Plotting the confusion matrix
plt.figure(figsize=(10, 7))
class_labels = ["No ADHD", "ADHD"]
sns.heatmap(cm, annot=True, fmt='g', cmap='Blues', xticklabels=class_labels, yticklabels=class_labels)
plt.title('Confusion Matrix')
plt.xlabel('Predicted labels')
plt.ylabel('True labels')
plt.show()

fpr, tpr, _ = roc_curve(y_test, best_model.predict_proba(X_test)[:, 1])
plt.plot(fpr, tpr)
plt.show()
