import tensorflow as tf
import os

frozen = './_frozen/DBR1.9.8-8000_frozen.pb'                              # path del grafo freezato
tflite_dir = './_tflite/'                                            # cartella per il modello .tflite
input_node_names_list = ['input']                                    # lista dei nomi dei nodi (strati) in input   [questo/i valore è preso dal file .txt (GENERATO da model2pbtxt.py) che contiene i nomi dei nodi del grafo]
output_node_names_list = ['build_network/Squeeze']                   # lista dei nomi dei nodi (strati) in output  [questo/i valore è preso dal file .txt (GENERATO da model2pbtxt.py) che contiene i nomi dei nodi del grafo]
input_shape = [[1, 128, 128, 3]]                                       # lista degli shape dei dati in input agli strati di input


def frozen2tflite(frozen, output_tflite_dir, input_node_names_list, input_shape, output_node_names_list):
    input_shapes = {}
    for i, input_node_name in enumerate(input_node_names_list):
        input_shapes[input_node_name] = input_shape[i]

    converter = tf.compat.v1.lite.TFLiteConverter.from_frozen_graph(
        frozen,
        input_node_names_list,
        output_node_names_list,
        input_shapes=input_shapes
    )

    tflite_model = converter.convert()
    tflite_path = os.path.join(output_tflite_dir, os.path.basename(frozen).replace('_frozen.pb','.tflite'))
    open(tflite_path,'wb').write(tflite_model)

    print('\n[INFO]: File '+ tflite_path + ' creato con successo!')

if __name__ == '__main__':
    frozen2tflite(frozen, tflite_dir, input_node_names_list, input_shape, output_node_names_list)
