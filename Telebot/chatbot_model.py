
# Packages to import.
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
import json
import pickle
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.optimizers import Adam,SGD
import random
lemmatizer = WordNetLemmatizer()

# Empty list-> words,tags and words n tags.
words = []
classes = []
documents = []
ignore_words = ['?', '!']
#loading the intents json file
data_file = open('intents.json').read()
#Loads data in Jason format
intents = json.loads(data_file)

# loop to add word from intents to words[], tags to classes[], and words and tags to documents[]
for intent in intents['intents']:
    for pattern in intent['patterns']:

        # tokenize each word
        w = word_tokenize(pattern)
        words.extend(w)
        # add documents in the corpus
        documents.append((w, intent['tag']))

        # add to our classes list
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

# lemmatize (find the root word) and covert the word to lower case.
words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
words = sorted(list(set(words)))
classes = sorted(list(set(classes)))

#creating a pickel files of words and tags.
pickle.dump(words, open('./words.pkl', 'wb'))
pickle.dump(classes, open('./classes.pkl', 'wb'))

training = []
# create an empty array for our output
output_empty_list = [0] * len(classes)


# training set, bag of words for each sentence
for doc in documents:
    # initialize our bag of words
    bag = []
    # list of tokenized words for the pattern
    pattern_words = doc[0]
    #print("doc[0]",doc)
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]
    #print("\n \t", pattern_words)
    # create our bag of words array with 1, if word match found in current pattern
    for w in words:
        #print("w is ",w)
        bag.append(1) if w in pattern_words else bag.append(0)
        #print("bag is ", bag)
    # output is a '0' for each tag and '1' for current tag (for each pattern)
    output_row = list(output_empty_list)
    output_row[classes.index(doc[1])] = 1
    training.append([bag, output_row])


# shuffle our features and turn into np.array
random.shuffle(training)
training = np.array(training)
# create train and test lists. X - patterns, Y - intents
train_x = list(training[:, 0])
train_y = list(training[:, 1])
print("Training data created")

# Create model - 3 layers. First layer 128 neurons, second layer 64 neurons and 3rd output layer contains number of
# neurons equal to number of intents to predict output intent with softmax

model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))

#Output Layer
model.add(Dense(len(train_y[0]), activation='softmax'))

# Compile model. Stochastic gradient descent with Nesterov accelerated gradient gives good results for this model
#sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9) #acuracy: 97.8
#adamOpti = Adam(lr = 0.01) #acuracy: 93.22

sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)  #acuracy: 98.7
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

# fitting and saving the model
hist = model.fit(np.array(train_x), np.array(train_y), epochs=120, batch_size=5, verbose=1)
model.save('chatbot_model.h5', hist)

print(f"{'*'*20} model created {'*'*20}")
