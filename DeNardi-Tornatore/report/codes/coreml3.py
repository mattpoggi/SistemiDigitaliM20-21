output_directory_path = './output'

supervisor = tf.train.Supervisor(logdir=output_directory_path)

with supervisor.managed_session() as session:
    # train the model here
    supervisor.saver.save(session, output_directory_path)
