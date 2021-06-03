import cv2
import numpy as np

#Classe Cane
class Cane:
    def __init__(self, tipo, filename, razza1, percent1, razza2, percent2):
        self.tipo = tipo         #tipo = { 'invalido', 'puro', 'misto' }
        self.filename = filename
        self.razza1 = razza1
        self.percent1 = percent1
        self.razza2 = razza2
        self.percent2 = percent2


def print_human_readable_dog_cli(dog):
    if (dog.tipo == 'invalido'):
      return ('In ' + dog.filename + ' non è stato riconosciuto un cane oppure non è stata riconosciuta una razza di cane nota.')
    elif (dog.tipo == 'puro'):
      return ('In ' + dog.filename + ' c\'è un cane di razza pura.\nRazza: ' + dog.razza1 + '\nPrecisione: %.1f'%(dog.percent1*100))
    elif (dog.tipo == 'misto'):
      return ('In ' + dog.filename + ' c\'è un cane di razza mista.\nRazza1: ' + dog.razza1 +'\nPrecisione: %.1f'%(dog.percent1*100)
      + '\n\nRazza2: ' + dog.razza2 + '\nPrecisione: %.1f'%(dog.percent2*100))


def print_human_readable_dog_deploy(dog):
    if (dog.tipo == 'invalido'):
      return ('Non è stato riconosciuto un cane oppure non è stata riconosciuta una razza di cane nota.')
    elif (dog.tipo == 'puro'):
      return ('Trovato un cane di razza pura.\nRazza: ' + dog.razza1 + '\nPrecisione: %.1f'%(dog.percent1*100))
    elif (dog.tipo == 'misto'):
      return ('Trovato un cane di razza mista.\nRazza1: ' + dog.razza1 +'\nPrecisione: %.1f'%(dog.percent1*100)
      + '\n\nRazza2: ' + dog.razza2 + '\nPrecisione: %.1f'%(dog.percent2*100))



def calc_score(res):
    """
    #res --> array formato così
    #0: [true_razza1, true_razza2, Cane] #--> Cane è il cane predetto dalla rete!
    #1: [true_razza1, true_razza2, Cane] #--> Cane è il cane predetto dalla rete!
    # ...
    #Se true_razza2 = None --> cane puro altrimenti incrocio


    -- Punteggio alla rete neurale --
    Indovinato razza pura o incrocio: 1 punto

    Se razza pura, indovinato la razza: 1 punto
    Se incrocio, per ciascuna razza incrocio indovinata: 0,5
    """

    totale = 0.
    for r in res:
        isPuro = False
        true_razza1 = r[0]
        true_razza2 = r[1]
        dog = r[2]

        if (true_razza2==None):
            isPuro = True

        if (isPuro and dog.tipo == 'puro'):
            totale += 1.
            if (true_razza1 == dog.razza1):
                totale += 1.
        elif (not isPuro and dog.tipo == 'misto'):
            totale += 1.
            if (true_razza1 == dog.razza1):
                totale += 0.5
            if (true_razza2 == dog.razza2):
                totale += 0.5

    return totale


def calc_score_top1(res, output_values):
    """
    -- Punteggio alla rete neurale --
    Indovinato razza: 1 punto
    """

    totale = 0
    for r in res:
        true_razza = r[0]
        array_predizioni = r[1]

        massimo = max(array_predizioni)
        indice_massimo = np.where(array_predizioni == massimo)[0][0]

        if (true_razza == output_values[indice_massimo]):
            totale += 1

    return totale


def calc_score_top5(res, output_values):
    """
    -- Punteggio alla rete neurale --
    Indovinato razza nelle prime 5 predette: 1 punto
    """

    totale = 0
    for r in res:
        true_razza = r[0]
        array_predizioni = r[1]
        breeds = output_values.to_numpy()

        top5 = []
        for i in range(5):
            massimo = np.max(array_predizioni)
            indice_massimo = np.where(array_predizioni == massimo)[0][0]

            top5.append(breeds[indice_massimo])

            array_predizioni = np.delete(array_predizioni, indice_massimo)
            breeds = np.delete(breeds, indice_massimo)

        if (true_razza in top5):
            totale += 1

    return totale


def get_dog_from_predictions(array_predizioni, output_values, filename):
    """
      Predizione della razza del cane (razza pura o incrocio)
      array_predizioni è un array di 120 razze con un valore percentuale predetto per ogni razza
    """
    output_values = output_values.to_numpy()

    massimo1 = np.max(array_predizioni)
    indice_massimo1 = np.where(array_predizioni == massimo1)[0][0]
    razza1 = output_values[indice_massimo1]

    array_predizioni = np.delete(array_predizioni, indice_massimo1)
    output_values = np.delete(output_values, indice_massimo1)

    massimo2 = np.max(array_predizioni)
    indice_massimo2 = np.where(array_predizioni == massimo2)[0][0]
    razza2 = output_values[indice_massimo2]

    dog = Cane('invalido', filename, razza1, massimo1, razza2, massimo2)

    limit = 1
    if (dog.percent1 < 0.7):
        dog.tipo = 'invalido'
    else:
        if (dog.percent1 >= 0.7 and dog.percent1 < 0.8):
            limit = 0.15 #15 %
        else:
          if (dog.percent1 >= 0.8 and dog.percent1 < 0.85):
              limit = 0.1 # 10 %
          else:
              if (dog.percent1 >= 0.85 and dog.percent1 < 0.9):
                  limit = 0.07 # 7 %
              else:
                  if (dog.percent1 >= 0.9 and dog.percent1 < 0.95):
                      limit = 0.04 # 4 %

        if (dog.percent2 >= limit):
            dog.tipo = 'misto'
        else:
            dog.tipo = 'puro'


    return dog



def resize_square_image_keep_ratio_border(img, desired_size):
    """
    img: img object cv2
    desired_size: intero
    """
    old_size = img.shape[:2] # old_size is in (height, width) format
    ratio = float(desired_size)/max(old_size)
    new_size = tuple([int(x*ratio) for x in old_size])

    # new_size should be in (width, height) format

    img = cv2.resize(img, (new_size[1], new_size[0]))

    delta_w = desired_size - new_size[1]
    delta_h = desired_size - new_size[0]
    top, bottom = delta_h//2, delta_h-(delta_h//2)
    left, right = delta_w//2, delta_w-(delta_w//2)

    color = [0, 0, 0]
    new_img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT,value=color)

    return new_img



def read_test_labels(labels_file):
    with open(labels_file,'r') as f:
        lines = f.readlines()

    matrix_labels = []
    for l in lines:
        split = l.strip()
        matrix_labels.append(split)
    return matrix_labels
