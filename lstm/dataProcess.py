import numpy as np
import pandas as pd
from keras.callbacks import EarlyStopping
from keras.layers import Embedding, SpatialDropout1D, LSTM, Dense
from keras.preprocessing.text import Tokenizer
from keras.preprocessing import sequence
from pandas import DataFrame
import codecs
from keras.models import Sequential
import matplotlib.pyplot as plt
from pylab import mpl
import jieba as jb
from sklearn.model_selection import train_test_split
import re
from tensorflow import keras

MAx_NB_WORDS = 50000
MAx_SEQUENCE_LENGTH = 250
EMBEDDING_DIM = 128

mpl.rcParams['font.sans-serif'] = ['SimHei']


# 定义删除除字母,数字，汉字以外的所有符号的函数
def remove_punctuation(line):
    line = str(line)
    if line.strip() == '':
        return ''
    rule = re.compile(u"[^a-zA-Z0-9\u4E00-\u9FA5]")
    line = rule.sub('', line)
    return line


def stopwordslist(filepath):
    stopwords = [line.strip() for line in open(filepath, 'r', encoding='utf-8').readlines()]
    return stopwords


def predict(text):
    txt = remove_punctuation(text)
    txt = [" ".join([w for w in list(jb.cut(txt)) if w not in stopwords])]
    seq = tokenizer.texts_to_sequences(txt)
    padded = sequence.pad_sequences(seq, maxlen=MAx_SEQUENCE_LENGTH)
    pred = model.predict(padded)
    first_level_id = pred.argmax(axis=1)[0]
    return first_level_id_df[first_level_id_df.first_level_id == first_level_id]['first_level'].values[0]


# 加载停用词
stopwords = stopwordslist("../StopWord.txt")

df = pd.read_csv('../labeledDomain01.csv', error_bad_lines=False,
                 # lineterminator='\n',
                 encoding='utf-8', sep=None)
df = df[['first_level', 'second_level', 'domain', 'title', 'description']]
# print("数据总量: %d ." % len(df))
# print(df.loc[[1997]].values[0][0])
# print(df.loc[[1997]].values[0][1])
# print(df.loc[[1997]].values[0][2])
# print(df.loc[[1997]].values[0][3])
# print(df.loc[[1997]].values[0][4])

# print(df.shape[1997])
# df.sample(10)
print("在first_level列 共有 %d 个空值." % df['first_level'].isnull().sum())
print("在description列共有 %d 个空值." % df['description'].isnull().sum())
df[df.isnull().values == True]
df = df[pd.notnull(df['description'])]
d = {'second_level': df['second_level'].value_counts().index, 'count': df['second_level'].value_counts()}
# d = {'first_level': df['first_level'].value_counts().index, 'count': df['first_level'].value_counts()}
df_level = pd.DataFrame(data=d).reset_index(drop=True)
df_level
# df_level.plot(x='first_level', y='count', kind='bar', legend=False, figsize=(20, 12))
# plt.xticks(size='small', rotation=68, fontsize=13)
# plt.title("一级分类分布")
# plt.ylabel('数量', fontsize=30)
# plt.xlabel('一级分类', fontsize=30)
df_level.plot(x='second_level', y='count', kind='bar', legend=False, figsize=(20, 12))
plt.xticks(size='small', rotation=68, fontsize=13)
plt.title("二级分类分布")
plt.ylabel('数量', fontsize=30)
plt.xlabel('二级分类', fontsize=30)
# plt.show()
# 分类转id 便于之后训练
df['first_level_id'] = df['first_level'].factorize()[0]
first_level_id_df = df[['first_level', 'first_level_id']].drop_duplicates().sort_values('first_level_id').reset_index(
    drop=True)
first_level_id = dict(first_level_id_df.values)
id_first_level = dict(first_level_id_df[['first_level_id', 'first_level']].values)
df['clean_description'] = df['description'].apply(remove_punctuation)
df.sample(10)
print(df.sample(10))
# 分词，并过滤停用词
df['cut_description'] = df['clean_description'].apply(lambda x: " ".join([w for w in list(jb.cut(x))
                                                                          if w not in stopwords]))
# print(df.head())
# 以上为预处理过程
tokenizer = Tokenizer(num_words=MAx_NB_WORDS, filters='!"#$%&()*+,-./:;<=>?@[\]^_`{|}~',
                      lower=True)
tokenizer.fit_on_texts(df['cut_description'].values)
word_index = tokenizer.word_index
print("共有 %s 个不相同的词语." % len(word_index))
x = tokenizer.texts_to_sequences(df['cut_description'].values)
# 填充x让 x的各列长度统一
x = sequence.pad_sequences(x, maxlen=MAx_SEQUENCE_LENGTH)

# 多类标签的onehot展开
y = pd.get_dummies(df['first_level_id'].values)

print(x.shape)
print(y.shape)

# 拆分测试集和训练集
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.10, random_state=42)
print(x_train.shape, y_train.shape)
print(x_test.shape, y_test.shape)
# y_train = y_train.values.reshape(y_train.shape[0])
# y_test = y_test.values.reshape(y_test.shape[0])
# y_train = keras.utils.to_categorical(y_train, 7)
# y_test = keras.utils.to_categorical(y_test, 7)

# 定义模型
model = Sequential()
model.add(Embedding(MAx_NB_WORDS, EMBEDDING_DIM, input_length=x.shape[1]))
model.add(SpatialDropout1D(0.4))
model.add(LSTM(64, dropout=0.4, recurrent_dropout=0.4))
# model.add(Dense(7, activation='softmax'))
# model.add(Dense(32, activation='sigmoid'))
# model.add(Dense(16, activation='sigmoid'))
model.add(Dense(7, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
print(model.summary())

# 训练数据
epochs = 5
batch_size = 64

history = model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size, validation_split=0.1,
                    callbacks=[EarlyStopping(monitor='val_loss',
                                             patience=3, min_delta=0.0001)])

plt.title("Loss")
plt.plot(history.history['loss'], label='train')
plt.plot(history.history['val_loss'], label='test')
plt.legend()
plt.show()

plt.title('Accuracy')
plt.plot(history.history['acc'], label='train')
plt.plot(history.history['val_acc'], label='test')
plt.legend()
plt.show()
