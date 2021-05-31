# Riconoscitore e risolutore di equazioni scritte a mano

Questo progetto tratta il riconoscimento di equazioni scritte a mano e la loro risoluzione. Le immagini prese in esame vengono prima segmentate carattere per carattere utilizzando OpenCV, per poi essere date in pasto al modello per ottenere le predizioni. Una volta ottenute le predizioni, è possibile risolvere le equazioni.

Il dataset utilizzato per il training è reperibile [qui](https://www.kaggle.com/xainano/handwrittenmathsymbols).

Viene prima effettuato il training tramite `training_nn.py`. Sono stati testati quattro tipi di modello, presenti in questa repository. In particolare:

- `model_v8`, che accetta un'immagine RGB, filtri: 16, 32, 64
```
model = tf.keras.Sequential([
  layers.experimental.preprocessing.Rescaling(1./255,
			input_shape=(img_height, img_width, 3)),
  layers.Conv2D(16, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(32, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(64, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Flatten(),
  layers.Dense(128, activation='relu'),
  layers.Dense(num_classes)
])
```

- `model_v9`, che accetta un'immagine RGB, filtri: 32, 32, 32
```
model = tf.keras.Sequential([
  layers.experimental.preprocessing.Rescaling(1./255,
			input_shape=(img_height, img_width, 3)),
  layers.Conv2D(32, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(32, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(32, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Flatten(),
  layers.Dense(128, activation='relu'),
  layers.Dense(num_classes)
])
```

- `model_v11`, che accetta un'immagine grayscale, filtri: 32, 32, 32
```
model = tf.keras.Sequential([
  layers.experimental.preprocessing.Rescaling(1./255,
			input_shape=(img_height, img_width, 1)),
  layers.Conv2D(32, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(32, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(32, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Flatten(),
  layers.Dense(128, activation='relu'),
  layers.Dense(num_classes)
])
```

- `model_v12`, che accetta un'immagine grayscale, filtri: 16, 32, 64
```
model = tf.keras.Sequential([
  layers.experimental.preprocessing.Rescaling(1./255,
			input_shape=(img_height, img_width, 1)),
  layers.Conv2D(16, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(32, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(64, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Flatten(),
  layers.Dense(128, activation='relu'),
  layers.Dense(num_classes)
])
```

Lo script `segmentation.py` esegue la segmentazione e la predizione su un'immagine, mentre `to_lite.py` converte un modello HDF5 in TensorflowLite.

Infine, il progetto `Eq` è l'applicazione Android che riceve in input un'immagine dalla galleria o dalla fotocamera, la segmenta, esegue le predizioni e permette di ottenere il risultato dell'equazione.