import json
from chatterbot import BotReinoAnimal
from chatterbot.trainers import ListTrainer

# Crear instancia de ChatBot
ReinoAnimal = BotReinoAnimal(
    'Reyno Animal Bot',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'Lo siento no entiendo lo que me dijo, podrías repetir lo que dijiste por favor',
            'maximum_similarity_threshold': 0.80
        }
    ],
    database_uri='sqlite:///ReinoAnimalBot.sqlite3'
) 

# Cargar datos de entrenamiento desde el archivo JSON combinado
with open('datos_de_entrenamiento/preguntas_respuestas_combinado.json', 'r', encoding='utf-8') as file:
    training_data = json.load(file)


# Entrenar al bot con las preguntas y respuestas
preguntas_entrenadas = set()  # Mantener un registro de las preguntas ya entrenadas
trainer = ListTrainer(ReinoAnimal)
for enfermedad, datos_enfermedad in training_data.items():
    for datos in datos_enfermedad:
        respuesta = datos['respuesta']
        for pregunta in datos['preguntas']:
            if pregunta not in preguntas_entrenadas:  # Verificar si la pregunta ya se entrenó
                trainer.train([pregunta, respuesta])
                preguntas_entrenadas.add(pregunta)  # Agregar la pregunta al conjunto de preguntas entrenadas
