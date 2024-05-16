# -*- coding: utf-8 -*-
"""Mini_report.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ZQDafnDIS4wk5KqtoQmn0Siy9gWOgGlX

# Calling all the libraries
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
from subprocess import check_output
import matplotlib.pyplot as plt
# %matplotlib inline

from keras.models import Sequential
from keras.layers import Dense
from keras.callbacks import ModelCheckpoint

seed = 42
np.random.seed(seed)

"""# Uploading dataset"""

from google.colab import files
uploaded = files.upload()

"""# Load Pima dataset"""

import io
pdata = pd.read_csv(io.BytesIO(uploaded['pima-indians-diabetes.csv']))
pdata.head()

"""# Dataset information or description"""

pdata.describe()

"""# Removing the 0-entries for some fields, as there should be no zero value"""

zero_fields = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']

def check_zero_entries(data, fields):
    """ List number of 0-entries in each of the given fields"""
    for field in fields:
        print('field %s: num 0-entries: %d' % (field, len(data.loc[ data[field] == 0, field ])))

check_zero_entries(pdata, zero_fields)

"""First - split into Train/Test,
The reason for doing this is because imputing whole dataset with average can influence the learning process. So, inorder to avoid biasness in testing and training. We will impute 0 with average values in training and testing dataset seperately.
"""

from sklearn.model_selection import train_test_split

features = list(pdata.columns.values)
features.remove('Outcome')
print(features)
X = pdata[features]
y = pdata['Outcome']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=0)

print(X_train.shape)
print(X_test.shape)

# lets fix the 0-entry for a field in the dataset with its mean value
def impute_zero_field(data, field):
    nonzero_vals = data.loc[data[field] != 0, field]
    avg = np.sum(nonzero_vals) / len(nonzero_vals)
    k = len(data.loc[ data[field] == 0, field])   # num of 0-entries
    data.loc[ data[field] == 0, field ] = avg
    print('Field: %s; fixed %d entries with value: %.3f' % (field, k, avg))

# Fix it for Train dataset
for field in zero_fields:
    impute_zero_field(X_train, field)

# double check for the Train dataset
check_zero_entries(X_train, zero_fields)

# Fix for Test dataset
for field in zero_fields:
    impute_zero_field(X_test, field)

# Ensure that fieldnames aren't included
X_train = X_train.values
y_train = y_train.values
X_test  = X_test.values
y_test  = y_test.values

tr1 = y_train[y_train==1]
tr0 = y_train[y_train==0]


print('Total number of ones in training dataset', tr1.shape)
print('Total number of zeros in training dataset',tr0.shape)



te1 = y_test[y_test==1]
te0 = y_test[y_test==0]

print('Total number of ones in testing dataset', te1.shape)
print('Total number of zeros in testing dataset',te0.shape)

NB_EPOCHS = 1000  # num of epochs to test for
BATCH_SIZE = 16

## Create our model
model = Sequential()

# 1st layer: input_dim=8, 12 nodes, RELU
model.add(Dense(12, input_dim=X_train.shape[1], activation='relu'))

# 2nd layer: 8 nodes, RELU
model.add(Dense(8, activation='relu'))
# output layer: dim=1, activation sigmoid
model.add(Dense(1, activation='sigmoid' ))

model.summary()

# Compile the model
model.compile(loss='binary_crossentropy',   # since we are predicting 0/1
             optimizer='adam',
             metrics=['accuracy'])

# checkpoint: store the best model
ckpt_model = 'pima-weights.best.hdf5'
checkpoint = ModelCheckpoint(ckpt_model,
                            monitor='val_accuracy',
                            verbose=1,
                            save_best_only=True,
                            mode='max')
callbacks_list = [checkpoint]

print('Start training...')
# train the model, store the results for plotting

history = model.fit(X_train,
                    y_train,
                    validation_data=(X_test, y_test),
                    epochs=NB_EPOCHS,
                    batch_size=BATCH_SIZE,
                    callbacks=callbacks_list,
                    verbose=1)

# Model accuracy
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model Accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'])
plt.ylim(0.55,0.85)
plt.savefig('accuracy.png')
plt.show()

# Model Losss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'])
plt.ylim(0.38,0.7)
plt.savefig('loss.png')
plt.show()

# print final accuracy
scores = model.evaluate(X_test, y_test, verbose=0)
print("%s: %.2f%%" % (model.metrics_names[1], scores[1]*100))

prediction = model.predict(X_test)

prediction[prediction > 0.5] = 1
prediction[prediction < 0.5] = 0
prediction[prediction == 0.5] = 1

import sklearn.metrics
import seaborn as sns

r = sklearn.metrics.confusion_matrix(y_test, prediction)
group_names = ['True Neg','False Pos','False Neg','True Pos']
group_counts = ['{0:0.0f}'.format(value) for value in r.flatten()]
labels = [f'{v1}\n{v2}' for v1, v2 in zip(group_names,group_counts)]
labels = np.asarray(labels).reshape(2,2)

sns.heatmap(r, annot=labels, fmt='', cmap='Blues')

results_path = 'results.png'
plt.savefig(results_path)

acc = sklearn.metrics.accuracy_score(y_test, prediction)
acc

precision = sklearn.metrics.precision_score(y_test, prediction, pos_label=1)
print(precision)

mcc = sklearn.metrics.matthews_corrcoef(y_test, prediction)
mcc