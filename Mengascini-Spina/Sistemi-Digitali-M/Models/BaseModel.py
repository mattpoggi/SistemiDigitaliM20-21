import time
from abc import ABC, abstractmethod
from contextlib import redirect_stdout
from pathlib import Path
from tensorflow.python.keras.backend import clear_session
from tensorflow.python.keras.models import Model
import tensorflow as tf
from Generators import DataGenerator


class BaseModel(ABC):
    """
        Base class defining the endpoint to use to interact with a model
    """

    def __init__(self, model_name: str, log_dir: Path = False, verbose: bool = True):
        """
        :param model_name: name of the model, used for logging and saving it
        :param log_dir: path of the dir in which to save the model and the tensorboard log
        :param verbose: boolean indicating if it is necessary to print extensive information
            in the console
        """

        # check if the log folder is a valid folder
        if log_dir is not None or log_dir != False:
            assert (log_dir.is_dir())
            self.logs = True
        else:
            self.logs = False

        # the verbose parameter controls how many log info will be printed in the console
        self.verbose = verbose

        # save the time of creation of this class, it will help us to uniquelly identify this specific train run
        self.str_time = time.strftime("%b%d%Y%H%M%S", time.gmtime())

        # save the model name and the directory in which to save the Logs
        self.name = model_name

        self.checkpoint_path = None

        if self.logs:
            self.parent_log_dir = log_dir

            # create the path of the log folder for this train run
            self.log_dir = self.parent_log_dir / "models" / self.name / self.str_time

            # create the log folder
            if not self.log_dir.is_dir():
                self.log_dir.mkdir(parents=True, exist_ok=True)

            # tensorboard has its own log directory
            self.tensorboard_log_dir = self.parent_log_dir / "tensorboard" / self.name / self.str_time

            #set the path to use to save a checkpoint
            self.checkpoint_path = self.log_dir / 'best_model.h5'

        # generating a unique name for the model depending on the time of its creation
        self.name_with_time = self.name + " " + self.str_time

    @abstractmethod
    def build_model(self, input_shape, output_shape) -> Model:
        """
        Function in charge of defining the model structure
        :param input_shape: tuple containing the shape of the data this model will recive as input
        :param output_shape: tuple containing the shape of the output produced by this model
        :return: Keras Sequential Model
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def input_shape(self) -> tuple:
        """
        This property returns the input shape of the model
        :return: tuple
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def output_shape(self) -> tuple:
        """
        This property returns the output shape of the model
        :return:
        """
        raise NotImplementedError

    def _get_callbacks(self) -> list:
        """
        Function defining all the callbacks for the given model and returning them as a list.
        In particular by default each model uses the following 3 callbacks
            - early stopping -> to stop the train early if the model has not improved in the past 10 epochs
            - checkpoint -> to save the model each time we find better weights
            - tensorboard -> to save the model Logs and be able to confront the models
        :return: list(keras.Callbacks)
        """
        callbacks = []

        if self.logs:
            callbacks += [
                tf.keras.callbacks.ModelCheckpoint(self.checkpoint_path, monitor='val_accuracy',
                    save_best_only=True,verbose=self.verbose),
                tf.keras.callbacks.TensorBoard(log_dir=self.tensorboard_log_dir),
            ]

        return callbacks

    def _on_before_train(self):
        """
        Set of actions to do right before the training phase
        :return:
        """
        self.training_start_time = time.time()


        if self.verbose:
            print("Model structure:")
            print(self.model.summary())
            print("The training phase of the model {} has started at:{}".format(self.name, self.training_start_time))

    def _on_after_train(self):
        """
        Set of actions to do right after the training phase
        :return:
        """
        self.training_time = time.time() - self.training_start_time

        if self.verbose:
            print("The model:{} has completed the training phase in: {}".format(self.name, self.training_time))

    def train_model(self, training_data: DataGenerator, validation_data: DataGenerator, epochs: int, loss_function,
                    optimizer=None,
                    save_model: bool = False, save_summary: bool = True):
        """
        Function in charge of training the model defined in the given class
        :param training_data: DataGenerator class, generating the training data
        :param validation_data: Datagenerator class, generating the validation data
        :param optimizer: optimizer to use during training (tf.keras.optimizers.Adam(0.0001)),
        :param loss_function: loss function to use
        :param epochs: number of epochs to run
        :param save_model: should the model be saved at the end of the training phase?
        :param save_summary: save the summary of the model into the log folder
        :return:
        """

        if optimizer == None:
            optimizer = tf.keras.optimizers.Adam(0.0001)

        # get the structure of the model as defined by the build function
        self.model = self.build_model(self.input_shape, self.output_shape)

        # compile the model
        self.model.compile(optimizer=optimizer, loss=loss_function, metrics=['accuracy'])

        # save the summary of the model if required
        if save_summary & self.logs:
            with open(self.log_dir / 'summary.txt', 'w') as f:
                with redirect_stdout(f):
                    self.model.summary()

        # execute "on before train" operations
        self._on_before_train()

        # train the model
        history = self.model.fit(training_data, steps_per_epoch=len(training_data), epochs=epochs,
                       validation_data=validation_data, validation_steps=len(validation_data),
                       callbacks=self._get_callbacks(), workers=4, shuffle=True)

        # execute "on after train" operations
        self._on_after_train()

        model_path = None
        # save the final model
        if save_model & self.logs:
            model_path = self.log_dir / "final-model.h5"
            self.model.save(model_path)
            if self.verbose:
                print("Model saved: {}".format(model_path))

        clear_session()
        return history.history,model_path,self.checkpoint_path