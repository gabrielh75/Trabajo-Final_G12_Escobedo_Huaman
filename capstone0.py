import pandas as pd #manipulación de datos en py
import numpy
import openpyxl
import random #aleatoriedad
import tensorflow as tf # machine learning
from tensorflow import keras #deep learning
from keras.layers import Dense #deep learning
import math #calculos matematicos

# Diccionario de sustituciones de caracteres débiles
sustituciones = {
    'a': ['a','4', '@', 'A'],
    'b': ['b','8', 'B'],
    'c': ['c','(', '[', 'C'],
    'e': ['e','3', 'E'],
    'f': ['f','1', '!', '|', 'I'],
    'g': ['g','6', 'G'],
    'h': ['h','H'],
    'i': ['i','1', '!', '|', 'I'],
    'j': ['j','J'],
    'k': ['k','k'],
    'l': ['l','1', '|', 'L'],
    'm': ['m','M'],
    'n': ['n','N'],
    'o': ['o','0', 'O'],
    'p': ['p','P'],
    'q': ['q','9', 'Q'],
    'r': ['r','R'],
    's': ['s','5', '$', 'S'],
    't': ['t','7', '+', 'T'],
    'u': ['u','U'],
    'v': ['v','V'],
    'w': ['w','W'],
    'x': ['x','X'],
    'y': ['y','Y'],
    'z': ['z','2','Z'],
    '0': ['0', 'o', 'O'],
    '1': ['1', 'l', 'I', '|'],
    '2': ['2', 'z', 'Z'],
    '3': ['3', 'e', 'E'],
    '4': ['4', 'a', 'A'],
    '5': ['5', 's', 'S'],
    '6': ['6', 'g', 'G'],
    '7': ['7', 't', 'T'],
    '8': ['8', 'b', 'B'],
    '9': ['9', 'q', 'Q']
}


def preprocess(contrasena):
    contrasena = str(contrasena).lower()
    return contrasena

def transformar_contrasena_debil(contrasena):
    nueva_contrasena = ''
    for caracter in contrasena:
        if caracter in sustituciones:
            sustitutos = sustituciones[caracter]
            sustituto = random.choice(sustitutos)
            nueva_contrasena += sustituto
        else:
            nueva_contrasena += caracter
    return nueva_contrasena

def convertir_a_arreglo_de_caracteristicas(contrasena):
    contrasena = contrasena.ljust(16,' ')
    arreglo_de_caracteristicas = []
    for caracter in contrasena:
        arreglo_de_caracteristicas.append(ord(caracter))
    return arreglo_de_caracteristicas

def crear_discriminador():
    modelo = keras.Sequential(
        [
            Dense(64, activation="relu", input_shape=(16,)),
            Dense(16, activation="relu"),
            Dense(1, activation="sigmoid"),
        ]
    )

    modelo.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return modelo

def entrenar_discriminador(discriminador, dataset_entrenamiento):
    X = []
    y = []

    dataset_entrenamiento['password'] = dataset_entrenamiento['password'].astype(str)

    for _, row in dataset_entrenamiento.iterrows():
        contrasena = row['password']
        etiqueta = row['strenght']

        contrasena = preprocess(contrasena)
        arreglo_caracteristicas = convertir_a_arreglo_de_caracteristicas(contrasena)
        X.append(arreglo_caracteristicas)
        y.append(etiqueta)

    X = tf.convert_to_tensor(X)
    y = tf.convert_to_tensor(y)

    discriminador.fit(X, y, epochs=10, batch_size=10)

def evaluar_contrasena(contrasena):
    contrasena = preprocess(contrasena)

    arreglo_caracteristicas = convertir_a_arreglo_de_caracteristicas(contrasena)
    arreglo_caracteristicas = tf.convert_to_tensor([arreglo_caracteristicas])
    prediccion = discriminador.predict(arreglo_caracteristicas)
    return prediccion[0][0] >= 0.5


def calcular_entropia(contrasena):
    caracteres_unicos = set(contrasena)
    longitud = len(contrasena)
    cantidad_caracteres_unicos = len(caracteres_unicos)

    probabilidad_caracter = 1.0 / cantidad_caracteres_unicos
    entropia = -1 * longitud * probabilidad_caracter * math.log2(probabilidad_caracter)

    return entropia


def calcular_probabilidad_descifrado(contrasena):
    # 3 meses en minutos
    tiempo_vigencia = 131400
    # 26 abecedario , 10 números , 31 caracteres especiales
    n_caracteres_posibles = 67
    # 5 intentos permitidos
    n_intentos = 5
    #longitud de contraseña
    longitud = len(contrasena)

    P=longitud*n_caracteres_posibles
    probabilidad = (tiempo_vigencia*n_intentos)/P

    return probabilidad

def main():

    contrasenaIng=[]
    codificaciones = []
    entropias = []
    probabilidades_descifrado = []
    durezas_ia = []

    dataset = pd.read_excel("D:\\Capstone0\\dataset_debiles.xlsx")
    dataset = dataset.sample(frac=1).reset_index(drop=True)
    dataset_entrenamiento = pd.read_excel("D:\\Capstone0\\dataset_entrenamiento.xlsx")
    dataset_entrenamiento = dataset_entrenamiento.sample(frac=1).reset_index(drop=True)

    entrenar_discriminador(discriminador,dataset_entrenamiento)


    while not dataset.empty:

        contrasena = dataset['password'].iloc[0]
        contrasena = contrasena.replace(" ","")
        contrasena_cod = transformar_contrasena_debil(preprocess(contrasena))

        intentos = 0
        while not evaluar_contrasena(contrasena_cod) and intentos < 3:
            contrasena_cod = transformar_contrasena_debil(preprocess(contrasena))
            intentos += 1

        dureza = evaluar_contrasena(contrasena_cod)
        entropia_cod = calcular_entropia(contrasena_cod)
        probabilidad_descifrado = calcular_probabilidad_descifrado(contrasena_cod)


        contrasenaIng.append(contrasena)
        codificaciones.append(contrasena_cod)
        entropias.append(entropia_cod)
        probabilidades_descifrado.append(probabilidad_descifrado)
        durezas_ia.append(dureza)

        dataset = dataset.iloc[1:]

    df_resultados = pd.DataFrame({
        'Contraseña Ingresada' : contrasenaIng,
        'Contraseña Codificada': codificaciones,
        'Entropía': entropias,
        'Probabilidad de Descifrado': probabilidades_descifrado,
        'Dureza IA': durezas_ia
    })
    ruta_guardado = "D:\\Capstone0\\resultados.xlsx"
    df_resultados.to_excel('resultados.xlsx', index=False)
    df_resultados.to_excel(ruta_guardado, index=False)

if __name__ == '__main__':
    discriminador = crear_discriminador()
    caracter_eliminar=''
    main()
