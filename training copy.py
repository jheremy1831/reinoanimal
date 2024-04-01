from chatterbot import BotReinoAnimal
from chatterbot.trainers import ListTrainer

# Creating ChatBot Instance
ReinoAnimal = BotReinoAnimal(
    'Reyno Animal Bot',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'Lo siento no entiendo lo que me dijo, podrias repetir lo que dijiste por favor',
            'maximum_similarity_threshold': 0.90
        }
    ],
    database_uri='sqlite:///ReinoAnimalBot.sqlite3'
) 

 # Training with Personal Ques & Ans 
training_data_quesans = open('datos_de_entrenamiento/PreguntasSimples.txt').read().splitlines()
training_data_enfermedad_1 = open('datos_de_entrenamiento/enfermedad_1.txt').read().splitlines()
training_data_enfermedad_2 = open('datos_de_entrenamiento/enfermedad_2.txt').read().splitlines()
training_data_enfermedad_3 = open('datos_de_entrenamiento/enfermedad_3.txt').read().splitlines()
training_data_enfermedad_4 = open('datos_de_entrenamiento/enfermedad_4.txt').read().splitlines()
training_data_enfermedad_5 = open('datos_de_entrenamiento/enfermedad_5.txt').read().splitlines()
training_data_otros = open('datos_de_entrenamiento/otras_preguntas.txt').read().splitlines()

training_data = training_data_quesans + training_data_enfermedad_1 + training_data_enfermedad_2 + training_data_enfermedad_3 + training_data_enfermedad_4 + training_data_enfermedad_5 + training_data_otros

trainer = ListTrainer(ReinoAnimal)
trainer.train(training_data)