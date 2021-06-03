import tensorflow as tf
import os
from tensorflow.python.tools import freeze_graph
from Network import DBR_Network


model = './trainedModel/DBR1.9.8-8000'                                 # modello addestrato
pbtxt = './_pbtxt/DBR1.9.8-8000.pbtxt'                                 # file .pbtxt
frozen_dir = './_frozen/'                                         # cartella di output per il grafo freezato
output_node_names = 'build_network/Squeeze'     # nome dello strato in uscita della rete
#Questo valore è il nome dello strato di output, preso dal file .txt (GENERATO da model2pbtxt.py) che contiene i nomi dei nodi del grafo
img_size = (128, 128, 3)


def pbtxt2frozen(model, pbtxt, output_node_names, output_frozen_dir):
    x = tf.placeholder(tf.float32,shape=[1,img_size[0],img_size[1],img_size[2]], name='input')
    network = DBR_Network(x=x, is_training=False)

    loader = tf.train.Saver()
    config = tf.ConfigProto(allow_soft_placement=True)
    with tf.Session(config=config) as session:
        loader.restore(session, model)

        pbtxt_name = os.path.basename(pbtxt)

        #save .pbtxt file as frozen .pb file
        freeze_graph.freeze_graph(input_graph=pbtxt,
                                  input_saver='',
                                  input_binary=False,
                                  input_checkpoint=model,
                                  output_node_names=output_node_names,
                                  restore_op_name="save/restore_all",
                                  filename_tensor_name='save/Const:0',
                                  output_graph=os.path.join(output_frozen_dir, pbtxt_name.replace('.pbtxt', '_frozen.pb')),
                                  clear_devices=True,
                                  initializer_nodes='')

        print('\n[INFO]: File '+ os.path.join(output_frozen_dir, pbtxt_name.replace('.pbtxt', '_frozen.pb')) + ' creato con successo!')

if __name__ == '__main__':
    pbtxt2frozen(model, pbtxt, output_node_names, frozen_dir)
