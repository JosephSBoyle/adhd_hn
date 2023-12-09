# Motivation

# Research Questions

### RQ1. Do users who report ADHD use different lexicon than control users?
How well can we predict if a given user has ADHD or not based on their language?

### RQ2. Is there a common 'ADHD lexicon' across Twitter and Hacker News: or these lexica distinct?
TBD.
# Modelling
### Data Collection
We collect a list of users who reported having ADHD using expressions such as:  `I was diagnosed` with ADHD`, `As an individual with ADD`, `I have ADHD. `The full regular expressions used are contained in the linked repository.

We then collect comments for each of the users who reported having ADHD, plus a pool of other randomly selected users.

Two well known correlates of ADHD are gender and age. Being young and being male are both predictive of a diagnosis of the condition. Since the age and gender of HN users is generally unknown we estimate these two variables using lexica dictionaries, derived from a dataset of Facebook comments [Sap. et al. 2014].  

Using these estimated gender and age characteristics we select a control group of equal size.

### Pre-processing
### Model Selection
### Error Analysis
# Conclusion

We analysed the comments from a sample of 1500 posters to the technology / startup oriented 
web forum Hackernews who reported having ADHD. We found that users with ADHD (did|did not) post at a statistically significant higher rate than control users of the same age and gender. We find a simple Logistic Regression classifier is able to meaningfully discriminate between our ADHD and control groups.