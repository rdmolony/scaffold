# Notebook to train a model

# +
import pickle

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier

# + tags=["parameters"]
upstream = ['features']
product = None
# -

df = pd.read_csv(str(upstream['features']))
X = df.drop('target', axis='columns')
y = df.target

X_train, X_test, y_train, y_test = train_test_split(X,
                                                    y,
                                                    test_size=0.33,
                                                    random_state=42)

# + tags=["model-training"]
clf = RandomForestClassifier(n_estimators=5)
clf.fit(X_train, y_train)
# -

y_pred = clf.predict(X_test)

print(classification_report(y_test, y_pred))

with open(product['model'], 'wb') as f:
    pickle.dump(clf, f)
