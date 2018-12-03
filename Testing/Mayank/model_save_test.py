from keras.models import load_model

model = load_model("../../NeuralNet/my_model.h5")
print(model.summary())
model.save('my_model.h5')