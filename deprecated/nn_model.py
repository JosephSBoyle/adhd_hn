import random

from datasets import Dataset
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from transformers import (AutoTokenizer, BertForSequenceClassification,
                          EvalPrediction, IntervalStrategy, SchedulerType,
                          Trainer, TrainingArguments)

import pandas as pd; import numpy as np; np.random.seed(7777)



### PREPROCESSING ###
# Load and preprocess the dataset
df = pd.read_csv("comments_stratified_balanced.csv")
df = df[["username", "reported_adhd", "comment"]]

users_train, users_temp = train_test_split(df["username"], train_size=0.8, stratify=df["reported_adhd"])
users_val,   users_test = train_test_split(users_temp,     train_size=0.5)

# Split concatenated comments into individual comments
# Note: three newlines is how I've concated the messages in the download script.. janky.

if False:
    # One row per comment
    df["comment"] = df["comment"].str.split("\n\n\n")
    # Explode the DataFrame - each comment becomes a separate row
    df = df.explode("comment")

if False:
    def split_text(text, length=2500):
        return [text[i:i+length] for i in range(0, len(text), length)]
    
    df['comment'] = df['comment'].apply(lambda x: split_text(x))
    df = df.explode("comment")

    comment_counts = df.groupby("username")["comment"].transform("count")
    df["sample_weight"] = 1 / comment_counts
else:
    df["sample_weight"] = 1

if False:
    # e.g 5.75x
    adhd_over_non_adhd = df[df["reported_adhd"] == 1]["sample_weight"].sum() / \
        df[df["reported_adhd"] == 0]["sample_weight"].sum()
    df[df["reported_adhd"] == 0]["sample_weight"] *= adhd_over_non_adhd
    
    assert df[df["reported_adhd"] == 1]["sample_weight"].sum() == \
        df[df["reported_adhd"] == 0]["sample_weight"].sum(), "WEIGHTS STILL ARENT EQUAL"


train_df = df[df['username'].isin(users_train)]
val_df   = df[df['username'].isin(users_val)]
test_df  = df[df['username'].isin(users_test)]

print("SPLIT SIZES: ", len(train_df), len(val_df), len(test_df))
print("AVERAGE SAMPLE WEIGHT: ",  df["sample_weight"].mean())
print("AVERAGE LABEL WEIGHTED: ", df["reported_adhd"].mean())
print("AVERAGE LABEL WEIGHTED: ", df["reported_adhd"] * df["sample_weight"])
print("RANDOM SAMPLE: ",  df.iloc[random.choice(df.index)]["comment"])

train_dataset = Dataset.from_pandas(pd.DataFrame({"text": train_df["comment"], "label": train_df["reported_adhd"], "weight": train_df["sample_weight"]}))
test_dataset  = Dataset.from_pandas(pd.DataFrame({"text": val_df  ["comment"], "label": val_df  ["reported_adhd"], "weight": val_df  ["sample_weight"]}))
val_dataset   = Dataset.from_pandas(pd.DataFrame({"text": test_df ["comment"], "label": test_df ["reported_adhd"], "weight": test_df ["sample_weight"]}))

# # Initialize tokenizer and model
# tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
# model     = BertForSequenceClassification.from_pretrained("bert-base-uncased")

from transformers import (LongformerForSequenceClassification,
                          LongformerTokenizer)

# Initialize tokenizer and model
tokenizer = LongformerTokenizer.from_pretrained("allenai/longformer-base-4096")
model     = LongformerForSequenceClassification.from_pretrained("allenai/longformer-base-4096")

def tokenize(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=512)

tokenized_train_dataset = train_dataset.map(tokenize, batched=True)
tokenized_val_dataset   = val_dataset  .map(tokenize, batched=True)

def compute_eval_metrics(eval_pred: EvalPrediction) -> dict:
    logits, labels = eval_pred
    predictions    = np.argmax(logits, axis=-1)
    return dict(accuracy=accuracy_score(labels, predictions), f1_score=f1_score(labels, predictions))

### Freeze base model's parameters ###
base_model = getattr(model, 'bert', getattr(model, "longformer", None))
for param in base_model.parameters():
    param.requires_grad = False
####

### TODO USE THE SAMPLE WEIGHTS FROM THE DF SOMEHOW!
training_args = TrainingArguments(
    max_steps                   = 10_000,
    per_device_train_batch_size = 4,
    per_device_eval_batch_size  = 4,
    warmup_steps                = 1_000,
    weight_decay                = 0.001,
    lr_scheduler_type           = SchedulerType.COSINE,
    eval_steps                  = 500,
    logging_steps               = 100,
    evaluation_strategy         = IntervalStrategy.STEPS,  # Evaluate every logging_steps
    logging_strategy            = IntervalStrategy.STEPS,
    output_dir                  = "./results",
    logging_dir                 = "./logs",
    load_best_model_at_end      = True,
)

# Initialize Trainer with validation dataset
trainer = Trainer(
    model           = model,
    args            = training_args,
    train_dataset   = tokenized_train_dataset,
    eval_dataset    = tokenized_val_dataset,  # Add validation dataset for evaluation
    compute_metrics = compute_eval_metrics,
)

# Train the model
trainer.train()

tokenized_test_dataset = test_dataset.map(tokenize, batched=True)
results                = trainer.evaluate(tokenized_test_dataset)

print(results)
breakpoint()