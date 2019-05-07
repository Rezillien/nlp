from pathlib import Path
from gensim.models import KeyedVectors
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE

model = KeyedVectors.load_word2vec_format(Path(".")/"skipgram"/"skip_gram_v100m8.w2v.txt", binary=False)

print("<2>")

print("sąd wysoki")

print(model.most_similar(["ne#Sąd_Najwyższy::noun"]))

print("trybunał konstytucyjny")

print(model.most_similar(["ne#Trybunał_konstytucyjny::noun"]))

print("kodeks cywilny")

print(model.most_similar(["ne#kodeks_cywilny::noun"]))

print("kpk")

print(model.most_similar(["kpk::noun"]))

print("sąd rejonowy")

print(model.most_similar(["ne#Sądu_rejonowego::noun"]))

print("szkoda")

print(model.most_similar(["szkoda::noun"]))

print("wypadek")

print(model.most_similar(["wypadek::noun"]))

print("kolizja")

print(model.most_similar(["kolizja::noun"]))

print("szkoda majątkowy")

print(model.most_similar(["szkoda_majątkowa::noun"]))

print("nieszczęście")

print(model.most_similar(["nieszczęście::noun"]))

print("rozwód")

print(model.most_similar(["rozwód::noun"]))

#4
print("<4>")

print(model.most_similar(["ne#Sąd_Najwyższy::noun", "konstytucja::noun"], ["kpc::noun"])[0:5])

print(model.most_similar(["pasażer::noun", "kobieta::noun"], ["mężczyzna::noun"])[0:5])

print(model.most_similar(["samochód::noun", "rzeka::noun"], ["droga::noun"])[0:5])

print("<5>")

highlighted=[
    "szkoda::noun",
    "szkoda::verb",
    "szkoda::adv",
    "strata::noun",
    "uszczerbek::noun",
    "szkoda_majątkowa::noun",
    "krzywdzić::verb",
    "krzywdzący::adj",
    "krzywdzić::noun",
    "krzywde::noun",
    "krzywde::xxx",
    "krzywdza::noun",
    "krzywdze::verb",
    "krzywde::adj",
    "krzywde::qub",
    "niesprawiedliwość::noun",
    "nieszczęście::noun",
    "nieszczęście::adv",
]

random_vectors = {
    key: model[key]
    for key in np.random.choice(list(model.vocab.keys()), 1000)
}

highlighted_vectors = {
    key: model[key]
    for key in highlighted
}

vectors = list(highlighted_vectors.items()) + list(random_vectors.items())
vectors_arrays = [vec[1] for vec in vectors]
transformed_vectors = TSNE().fit_transform(vectors_arrays)

x = []
y = []
for vec in transformed_vectors:
    x.append(vec[0])
    y.append(vec[1])

plt.figure(figsize=(16, 16))


for i in range(len(transformed_vectors)):
    plt.scatter(x[i], y[i])
    if i < len(list(highlighted_vectors)):
        plt.annotate(list(highlighted_vectors.keys())[i], xy=(x[i], y[i]),
                     color='red')
    else:
        plt.annotate(list(random_vectors.keys())[i-len(list(highlighted_vectors))], xy=(x[i], y[i]),
                     color='blue')
plt.show()



