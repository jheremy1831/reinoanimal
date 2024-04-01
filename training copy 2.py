import json
from chatterbot import BotReinoAnimal
from chatterbot.trainers import ListTrainer

# Crear una instancia del chatbot
ReinoAnimal = BotReinoAnimal(
    'Reyno Animal Bot',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'Lo siento no entiendo lo que me dijo, ¿podrías repetirlo por favor?',
            'maximum_similarity_threshold': 0.90
        }
    ],
    database_uri='sqlite:///ReinoAnimalBot.sqlite3'
) 

# Entrenar con datos de entrenamiento
training_data_quesans = open('datos_de_entrenamiento/respaldo/PreguntasSimples.txt').read().splitlines()
training_data_enfermedad_1 = open('datos_de_entrenamiento/respaldo/enfermedad_1.txt').read().splitlines()
training_data_enfermedad_2 = open('datos_de_entrenamiento/respaldo/enfermedad_2.txt').read().splitlines()
training_data_enfermedad_3 = open('datos_de_entrenamiento/respaldo/enfermedad_3.txt').read().splitlines()
training_data_enfermedad_4 = open('datos_de_entrenamiento/respaldo/enfermedad_4.txt').read().splitlines()
training_data_enfermedad_5 = open('datos_de_entrenamiento/respaldo/enfermedad_5.txt').read().splitlines()
training_data_otros = open('datos_de_entrenamiento/respaldo/otras_preguntas.txt').read().splitlines()

training_data_por_enfermedad = {
    "Enfermedad 1": training_data_enfermedad_1,
    "Enfermedad 2": training_data_enfermedad_2,
    "Enfermedad 3": training_data_enfermedad_3,
    "Enfermedad 4": training_data_enfermedad_4,
    "Enfermedad 5": training_data_enfermedad_5
}

training_data = (
    training_data_quesans + 
    training_data_enfermedad_1 + 
    training_data_enfermedad_2 + 
    training_data_enfermedad_3 + 
    training_data_enfermedad_4 + 
    training_data_enfermedad_5 + 
    training_data_otros
)

trainer = ListTrainer(ReinoAnimal)
trainer.train(training_data)

# Convertir el contenido por enfermedad en formato JSON
json_data_por_enfermedad = json.dumps(training_data_por_enfermedad, indent=4)

# Escribir el contenido JSON en un archivo
with open('ReinoAnimal_por_enfermedad.json', 'w') as json_file:
    json_file.write(json_data_por_enfermedad)

# Alternativamente, para imprimir el JSON en la salida estándar
print(json_data_por_enfermedad)
