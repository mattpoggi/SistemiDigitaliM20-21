self.input_shape = (192, 9, 1)
self.num_classes = 21
self.num_strings = 6

def build_model(self):
    model = Sequential()
    model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=self.input_shape))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))   
    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(self.num_classes * self.num_strings))
    model.add(Reshape((self.num_strings, self.num_classes)))
    model.add(Activation(self.softmax_by_string))

    model.compile(loss=self.catcross_by_string, optimizer=Adadelta(), metrics=[self.avg_acc])

    self.model = model