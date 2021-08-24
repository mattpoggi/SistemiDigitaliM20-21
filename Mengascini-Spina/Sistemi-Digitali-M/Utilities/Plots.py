import matplotlib.pyplot as plt
import numpy

def plot_model_data(history,keys:tuple,labels:tuple,title = ""):
    plt.plot(history[keys[0]])
    plt.plot(history[keys[1]])
    plt.title(title)
    plt.ylabel(labels[0])
    plt.xlabel(labels[1])
    plt.legend(("Accuracy", "Val_accuracy"), loc='upper left')
    plt.show()

