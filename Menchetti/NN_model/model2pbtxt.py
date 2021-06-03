import tensorflow as tf
import os
from Network import DBR_Network


model = './trainedModel/DBR1.9.8-8000'          # modello addestrato
pbtxt_dir = './_pbtxt/'                    # cartella di output per il file .pbtxt
img_size = (128, 128, 3)

def model2pbtxt(model, output_pbtxt_dir):
    x = tf.placeholder(tf.float32,shape=[1,img_size[0],img_size[1],img_size[2]], name='input')
    network = DBR_Network(x=x, is_training=False)

    loader = tf.train.Saver()
    config = tf.ConfigProto(allow_soft_placement=True)
    with tf.Session(config=config) as session:
        loader.restore(session, model)

        model_name = os.path.basename(model)
        pbtxt_file = model_name + '.pbtxt'
        txt_file =   model_name + '_node_names.txt'

        #save as .pbtxt file
        graph_def = session.graph.as_graph_def()
        tf.train.write_graph(graph_def, output_pbtxt_dir, pbtxt_file, as_text=True)

        print('\n[INFO]: File '+ os.path.join(output_pbtxt_dir, pbtxt_file) + ' creato con successo!')


        #save node names to .txt file
        with open(os.path.join(output_pbtxt_dir, txt_file),'w') as f:
            f.write('## Lista dei nomi dei nodi del grafo:\n\n')
            for node in graph_def.node:
                f.write(node.name + '\n')

            print('\n[INFO]: File '+ os.path.join(output_pbtxt_dir, txt_file) + ' creato con successo!')



if __name__ == '__main__':
    model2pbtxt(model, pbtxt_dir)
