#%% DATOS CARATULA
"""
Laboratorio de datos - Verano 2025
Trabajo Práctico N° 2

Integrantes:
- Sebastian Ceffalotti - sebastian.ceffalotti@gmail.com
- Aaron Cuellar - aaroncuellar2003@gmail.com
- Rodrigo Coppa - rodrigo.coppa98@gmail.com

Descripción:


Detalles técnicos:
abceslluevE
"""
# %% IMPORTACION DE LIBRERIAS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix
from sklearn import tree

#%% DECLARACION DE FUNCIONES
#%% FUNCION QUE CALCULA LA INTENSIDAD PROMEDIO DE UN DIGITO
def img_promedio_digito(datos, digito):
    datos_digito = datos[datos["labels"] == digito].drop(columns = "labels")
    img_promedio = np.sum(datos_digito, axis = 0)/len(datos_digito)
    return img_promedio
#%% FUNCION QUE CALCULA LA DESVIACION ESTANDAR PROMEDIO DE UN DIGITO
def img_std_promedio_digito(datos, digito):
    # Filtra los datos para el dígito específico y elimina la columna de etiquetas
    datos_digito = datos[datos["labels"] == digito].drop(columns="labels")
    
    # Calcula la desviación estándar a lo largo del eje 0 (para cada píxel)
    std_por_pixel = np.std(datos_digito, axis=0)
    
    # Devuelve la desviación estándar por píxel (no el promedio)
    return std_por_pixel
#%% FUNCION PARA GRAFICAR 15 IMAGENES ALEATORIAS DE UN DIGITO
def graficarMuestraDigitos(digito, semilla):
    # selecciono las imágenes del dígito
    digitos = X[labels == digito]
    
    # elijo 15 imágenes aleatorias
    muestras = digitos.sample(15, random_state=semilla)
    imagenes = muestras.values.reshape(15, 28, 28)
    
    # Grafico
    fig, axes = plt.subplots(nrows=3, ncols=5, figsize=(10, 5))
    
    indice = 0
    num_filas = axes.shape[0]
    num_columnas = axes.shape[1]
    for i in range(num_filas):
        for j in range(num_columnas):
            axes[i, j].imshow(imagenes[indice], cmap='gray')
            axes[i, j].axis('off')
            indice += 1
    plt.suptitle(f"Ejemplos de imagenes del digito {digito}", fontsize = 18)
    plt.show()
#%% FUNCION QUE CALCULA LA POSICION DE LA COLUMNA DE UN PIXEL DE ACUERDO A SUS COORDENADAS
def obtenerPosColumna(posicion):
    fila, columna = posicion[0], posicion[1]
    return 28*(fila-1) + columna - 1 # resto porque arranca en 0 (? chequear esto
#%% FUNCION QUE ENTRENA UN KNN CON LOS PIXELES SELECCIONADOS
def entrenar_modelo(X_train_seleccionado, X_test_seleccionado, y_train, y_test, titulo):
    rango_k = np.arange(1,25,1)
    
    accuracy = []
    precision = []
    recall = []
    
    # pruebo diferentes valores de k
    for k in rango_k:
        knn = KNeighborsClassifier(n_neighbors=k)
        knn.fit(X_train_seleccionado, y_train)
        # veo las predicciones
        y_pred = knn.predict(X_test_seleccionado)
        # Calculo las metricas
        accuracy.append(accuracy_score(y_test, y_pred))
        precision.append(precision_score(y_test, y_pred))
        recall.append(recall_score(y_test, y_pred))
    # Grafico la precisión en función de k
    plt.figure(figsize=(10, 6))
    plt.plot(rango_k, accuracy, marker='o', linestyle='--', color='r', label = "accuracy")
    plt.plot(rango_k, precision, marker='o', linestyle='--', color='g', label = "precision")
    plt.plot(rango_k, recall, marker='o', linestyle='--', color='b', label = "recall")
    
    plt.title(titulo)
    plt.xlabel('Número de vecinos (k)')
    plt.ylabel('valor de metrica')
    plt.legend()
    plt.xticks(rango_k)  
    plt.grid(True)
    plt.show()
#%% FUNCION QUE ENTRENA UN ARBOL SEGUN HIPERPARAMETROS ELEGIDOS, CRITERIO Y MAXIMA PROFUNDIDAD
def EntrenarArbol(alturas, kf, criterio):
    # matrices donde almacenar los resultados
    resultados_accuracy = np.zeros((nsplits, len(alturas)))
    resultados_precision = np.zeros((nsplits, len(alturas)))
    resultados_recall = np.zeros((nsplits, len(alturas)))
    
    # en cada folds, entrenamos cada modelo y guardo todo en las matrices de resultados
    for i, (train_index, test_index) in enumerate(kf.split(X_dev, y_dev)):
        kf_X_train, kf_X_test = X_dev.iloc[train_index], X_dev.iloc[test_index]
        kf_y_train, kf_y_test = y_dev.iloc[train_index], y_dev.iloc[test_index]
        
        for j, hmax in enumerate(alturas):
            # entreno al arbol
            arbol = tree.DecisionTreeClassifier(max_depth=hmax, criterion=criterio)
            arbol.fit(kf_X_train, kf_y_train)
            
            # hago la prediccion y calculo las metricas
            pred = arbol.predict(kf_X_test)
            accuracy = accuracy_score(kf_y_test, pred)
            # se usa macro para multiclase
            precision = precision_score(kf_y_test, pred, average='macro')
            recall = recall_score(kf_y_test, pred, average='macro')  
            
            # guardo los resultados
            resultados_accuracy[i, j] = accuracy
            resultados_precision[i, j] = precision
            resultados_recall[i, j] = recall
    
    return resultados_accuracy, resultados_precision, resultados_recall
    
# %% LECTURA DE ARCHIVOS

#rutas
_ruta_actual = os.getcwd()
_ruta_mnistc = os.path.join(_ruta_actual, 'mnist_c_fog_tp.csv')

# lectura mnistc, con el index_col podes decirle que columna usar de indice :)
mnistc = pd.read_csv(_ruta_mnistc, index_col = 0)
labels = mnistc["labels"]
# Guardo los pixeles en X 
X = mnistc.drop(columns = ["labels"]) 

#%% EJERCICIO 1.a
#%% GRAFICO LA IMAGEN PROMEDIO DE TODOS LOS DIGITOS

fig, axes = plt.subplots(3, 5, figsize=(12, 8))
axes = axes.flatten()
suma_todos_digitos = np.zeros((28, 28))

for digito in range(0,10):
    img_prom = img_promedio_digito(mnistc, digito)
    img = np.array(img_prom).reshape((28,28))
    suma_todos_digitos += img
    
    im = axes[digito].imshow(img, cmap='inferno')
    axes[digito].set_title(f"Digito {digito}")

# promedio de todos los digitos
suma_todos_digitos = suma_todos_digitos/10

# oculto ejes vacios y muestro el promedio entre todos los digitos
for i in [10, 11, 13, 14]:
    axes[i].axis('off')
axes[12].imshow(suma_todos_digitos, cmap='inferno')
axes[12].set_title("Suma de todos los dígitos")

fig.suptitle("Promedio de intensidad por dígito", fontsize=18)
cax = fig.add_axes([0.92, 0.15, 0.02, 0.7])  
cbar = fig.colorbar(im, cax=cax)
cbar.set_label("Intensidad promedio", fontsize=14)

#%% GRAFICO LA REGION DE LOS PIXELES MENOS RELEVANTES

umbral = 100 # lo elijo arbitrariamente viendo la imagen anterior
# creo una mascara binaria para graficar
mascara = suma_todos_digitos >= umbral
pixeles_menores_100 = np.sum(suma_todos_digitos < umbral)

print(f"Porcentaje de píxeles con intensidad menor a 100: {100*pixeles_menores_100/784}")
plt.imshow(mascara, cmap='gray')
plt.title("Píxeles con intensidad menor a 100 (negros)")
plt.show()
#%% GRAFICO LA IMAGEN DE LA DESVIACION ESTANDAR PROMEDIO DE TODOS LOS DIGITOS (QUIZAS SACARLO)

# Esto si no los usamos quizas habria que sacarlo
fig, axes = plt.subplots(2, 5, figsize=(12, 6))
axes = axes.flatten()
for digito in range(0,10):
    std_por_pixel = img_std_promedio_digito(mnistc, digito)
    img_std = np.array(std_por_pixel).reshape((28, 28))
    
    im = axes[digito].imshow(img_std, cmap='inferno')
    axes[digito].set_title(f"Digito {digito}")
    
fig.suptitle("Promedio de desviacion estandar por dígito", fontsize=18)
cax = fig.add_axes([0.92, 0.15, 0.02, 0.7])  
cbar = fig.colorbar(im, cax=cax)
cbar.set_label("Desviacion estandar promedio", fontsize=14)
#%% EJERCICIO 1.b
#%% CALCULO LAS DISTANCIAS ENTRE LAS IMAGENES PROMEDIO DE CADA DIGITO
# pienso cada imagen como un vector en R^784, entonces la distancia 
# es la norma de la diferencia entre dos vectores

imgs_promedio = {}
for digito in range(0,10):
    imagenes_digito = mnistc[mnistc["labels"] == digito].drop(columns="labels")
    imgs_promedio[digito] = np.mean(imagenes_digito, axis=0)

# creo una matriz donde guardar las distancias promedio entre cada digito, y las guardo
distancias = np.zeros((10, 10))  
for i in range(10):
    for j in range(10):
        distancias[i, j] = np.linalg.norm(imgs_promedio[i] - imgs_promedio[j])

distancias = distancias.astype(int) 
sns.heatmap(distancias, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Digito')
plt.ylabel('Digito')
plt.title('Matriz de distancias entre imagenes')
plt.show()

#%% EJERCICIO 1.c
#%% GRAFICO 15 MUESTRAS ALEATORIAS DE CADA DIGITO, EN TODOS LOS DIGITOS HAY MUCHA VARIACION
plt.figure(figsize=(10, 10))
for digito in range(0,10):
    graficarMuestraDigitos(digito,7)
    
#%% EJERCICIO 2
#%% EXTRAIGO LOS DATOS DE LOS 0 Y 1, VEO EL BALANCE Y SEPARO EN TRAIN Y TEST
datos = mnistc[mnistc["labels"].isin([0, 1])]
labels_bin = datos["labels"]

# Cuento y veo el balance de clases
contador = labels_bin.value_counts()
print(f"Hay {contador[0]} ceros")
print(f"hay {contador[1]} unos")
print("No esta balanceada la cantidad de clases, por eso las balanceo")

# separo los datos en TRAIN y TEST, hago 80 % train y el resto para test,
# manteniendo el balance de clase

X_train, X_test, y_train, y_test = train_test_split(datos, labels_bin,
test_size = 0.2, stratify = labels_bin, random_state = 160)

X_train = X_train.drop(columns="labels")
X_test = X_test.drop(columns = "labels")
#%% GRAFICO LOS PROMEDIOS DEL 0, EL 1 Y SU RESTA. POR INSPECCION DECIDO QUE PIXELES USAR

plt.figure(figsize=(12, 6))
img_prom_0 = img_promedio_digito(datos, 0)
plt.subplot(1, 3, 1)
plt.imshow(np.array(img_prom_0).reshape((28, 28)), cmap='gray')
plt.title("Promedio del 0")

img_prom_1 = img_promedio_digito(datos, 1)
plt.subplot(1, 3, 2)  
plt.imshow(np.array(img_prom_1).reshape((28, 28)), cmap='gray')
plt.title("Promedio del 1")

plt.subplot(1, 3, 3)  
resta = np.abs(img_prom_1-img_prom_0)
plt.imshow(np.array(resta).reshape((28, 28)), cmap='gray')
plt.title("Resta")

plt.tight_layout()
plt.show()

"""
Viendo las imagenes elijo pixeles de manera arbitraria, 
elijo el del centro, uno a la izquierda y otro a la derecha por ejemplo
"""   
#%% ENTRENO EL MODELO KNN ELIGIENDO 1 PIXEL ARBITRARIAMENTE, EL CENTRAL

pixeles_seleccionados = [[14, 14]]
columnas_pixeles = []
for pixel in pixeles_seleccionados:
    columnas_pixeles.append(obtenerPosColumna(pixel))

X_train_seleccionado = X_train.iloc[:, columnas_pixeles].values
X_test_seleccionado = X_test.iloc[:, columnas_pixeles].values

entrenar_modelo(X_train_seleccionado, X_test_seleccionado, y_train, y_test, "Metricas en funcion de k usando 1 pixel")
# Este da una accuracy de cerca del 50 %, es como tirar una moneda
#%% ENTRENO EL MODELO KNN ELIGIENDO 3 PIXELES ARBITRARIAMENTE

pixeles_seleccionados = [[8, 14], [14, 14], [22, 14]]
columnas_pixeles = []
for pixel in pixeles_seleccionados:
    columnas_pixeles.append(obtenerPosColumna(pixel))

X_train_seleccionado = X_train.iloc[:, columnas_pixeles].values
X_test_seleccionado = X_test.iloc[:, columnas_pixeles].values

entrenar_modelo(X_train_seleccionado, X_test_seleccionado, y_train, y_test, "Metricas en funcion de k usando 3 pixeles")

#%% ENTRENO EL MODELO KNN ELIGIENDO 15 PIXELES ARBITRARIAMENTE
pixeles_seleccionados = [[17, 16], [14, 14], [11, 10], [8, 14], [11,14], [14, 14], [18,14], [22, 14], [10,15], [24,13],
                         [19, 10], [19, 12], [15, 1], [19, 8], [15, 2]]
columnas_pixeles = []
for pixel in pixeles_seleccionados:
    columnas_pixeles.append(obtenerPosColumna(pixel))

X_train_seleccionado = X_train.iloc[:, columnas_pixeles].values
X_test_seleccionado = X_test.iloc[:, columnas_pixeles].values

entrenar_modelo(X_train_seleccionado, X_test_seleccionado, y_train, y_test, "Metricas en funcion de k usando 15 pixeles")

# como cambia mucho eligiendo cuales pixeles se usan, veo de usar como atributos las distancias a  la imagen promedio del 0 y el 1
#%% PREPARO LOS DATOS PARA ENTRENAR UN MODELO BASANDOSE EN DISTANCIAS

# obtengo la imagen promedio del 0 y el 1
imgs_promedio = {}
for digito in range(0,2):
    imagenes_digito = mnistc[mnistc["labels"] == digito].drop(columns="labels")
    imgs_promedio[digito] = np.mean(imagenes_digito, axis=0)
    
# calculo las distancias en train y test respecto al promedio del 0 y el 1
distancias_al_0_train = np.linalg.norm(X_train - imgs_promedio[0], axis=1)
distancias_al_1_train = np.linalg.norm(X_train - imgs_promedio[1], axis=1)
distancias_al_0_test = np.linalg.norm(X_test - imgs_promedio[0], axis=1)
distancias_al_1_test = np.linalg.norm(X_test - imgs_promedio[1], axis=1)
# agrego las distancias a los dataframes
X_train_dist = X_train.copy()
X_test_dist = X_test.copy()
X_train_dist["distancia_al_0"] = distancias_al_0_train
X_train_dist["distancia_al_1"] = distancias_al_1_train
X_test_dist["distancia_al_0"] = distancias_al_0_test
X_test_dist["distancia_al_1"] = distancias_al_1_test
#%% ENTRENO EL MODELO KNN, MIRO LA DISTANCIA DE CADA IMAGEN A LA PROMEDIO DE 0 Y 1

X_train_seleccionado = X_train_dist[["distancia_al_0", "distancia_al_1"]]
X_test_seleccionado = X_test_dist[["distancia_al_0", "distancia_al_1"]]
entrenar_modelo(X_train_seleccionado, X_test_seleccionado, y_train, y_test, "Metricas en funcion de k basandose en distancias")

# Mejoran bastante los resultados para usar solo dos valores, aunque requiere un preprocesamiento de los datos.
# Voy a usar un arbol para que encuentre los pixeles mas relevantes, asi uso esos para un nuevo KNN

#%% ENTRENO UN ARBOL PARA VER CUALES CONSIDERA COMO LOS PIXELES MAS IMPORTANTES

arbol = tree.DecisionTreeClassifier(max_depth=10, random_state=160)
arbol.fit(X_train, y_train)
# veo la prediccion
y_pred = arbol.predict(X_test)

# calculo las metricas para ver el rendimiento del modelo
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)

print(f"Accuracy: {accuracy:.2f}")
print(f"Precision: {precision:.2f}")
print(f"Recall: {recall:.2f}")
print("Matriz de confusión:")
print(confusion_matrix(y_test, y_pred))

# se puede extraer la importancia de cada atributo en el arbol, lo hago y armo una matriz
importancia_pixeles = arbol.feature_importances_
importancia_matriz = importancia_pixeles.reshape(28, 28)

# grafico la importancia de cada pixel en una imagen de 28x28
plt.figure(figsize=(8, 8))
plt.imshow(importancia_matriz, cmap='gray', interpolation='nearest')
plt.colorbar(label="Importancia")
plt.title("Importancia de los pixeles segun ubicacion")
plt.xlabel("Numero de columna")
plt.ylabel("Numero de fila")
plt.show()

# me quedo con los indice de mayor a menor importancia de los pixeles
pixeles_relevantes = np.argsort(importancia_pixeles)[::-1]  
print("Pixeles mas relevantes:", pixeles_relevantes[:10]) 
#%% USO LOS MEJORES 3 PIXELES SEGUN EL ARBOL
X_train_seleccionado = X_train_dist[["406","400","318"]]
X_test_seleccionado = X_test_dist[["406","400","318"]]
entrenar_modelo(X_train_seleccionado, X_test_seleccionado, y_train, y_test, "Metricas en funcion de los pixeles mas relevantes segun un arbol")
  
#%% ACA COMIENZA EL EJERCICIO 3
#%% DIVIDO LOS DATOS EN DEV Y HELD OUT, DEFINO PARAMETROS DE ENTRENAMIENTO

X_dev, X_heldout, y_dev, y_heldout = train_test_split(X, labels, test_size=0.2, random_state=160, stratify=labels)

alturas = [1,2,3,4,6,8,10]  # alturas del arbol
nsplits = 3  # numero de folds
# generamos los folds, stratifiedkfold permite dividir de forma balanceada los folds
kf = StratifiedKFold(n_splits=nsplits, shuffle=True, random_state=7)

#%% ENTRENO ARBOLES USANDO GINI
resultados_accuracy, resultados_precision, resultados_recall = EntrenarArbol(alturas, kf, "gini")

# calculo el promedio de todos los folds
scores_accuracy = resultados_accuracy.mean(axis=0)
scores_precision = resultados_precision.mean(axis=0)
scores_recall = resultados_recall.mean(axis=0)

# grafica las métricas
plt.plot(alturas, scores_accuracy, marker='o', linestyle='--', color='r', label="Accuracy")
plt.plot(alturas, scores_precision, marker='o', linestyle='--', color='g', label="Precision")
plt.plot(alturas, scores_recall, marker='o', linestyle='--', color='b', label="Recall")
plt.xlabel("Profundidad maxima")
plt.ylabel("Metrica")
plt.title("Metricas en funcion de la profundidad usando GINI")
plt.legend()
plt.grid(True)
plt.show()

#%% ENTRENO ARBOLES USANDO ENTROPIA
resultados_accuracy, resultados_precision, resultados_recall = EntrenarArbol(alturas, kf, "entropy")

# calculo el promedio de todos los folds
scores_accuracy = resultados_accuracy.mean(axis=0)
scores_precision = resultados_precision.mean(axis=0)
scores_recall = resultados_recall.mean(axis=0)

# Graficar las métricas
plt.plot(alturas, scores_accuracy, marker='o', linestyle='--', color='r', label="Accuracy")
plt.plot(alturas, scores_precision, marker='o', linestyle='--', color='g', label="Precision")
plt.plot(alturas, scores_recall, marker='o', linestyle='--', color='b', label="Recall")
plt.xlabel("Profundidad maxima")
plt.ylabel("Metrica")
plt.title("Metricas en funcion de la profundidad usando ENTROPIA")
plt.legend()
plt.grid(True)
plt.show()

#%% entreno el modelo elegido en el conjunto dev entero para la mejor profundidad
mejor_profundidad = 10
mejor_criterio = "entropy"
arbol_elegido = tree.DecisionTreeClassifier(max_depth=mejor_profundidad, criterion=mejor_criterio)
arbol_elegido.fit(X_dev, y_dev)

# Predecir en el conjunto de validación (held-out)
y_pred = arbol_elegido.predict(X_heldout)

# Calcular las métricas finales
score_accuracy = accuracy_score(y_heldout, y_pred)
score_precision = precision_score(y_heldout, y_pred, average='macro')
score_recall = recall_score(y_heldout, y_pred, average='macro')

print(f"Accuracy del arbol con depth {mejor_profundidad} en HELD OUT: {score_accuracy}")
print(f"Precision del arbol con depth {mejor_profundidad} en HELD OUT: {score_precision}")
print(f"Recall del arbol con depth {mejor_profundidad} en HELD OUT: {score_recall}")

# Matriz de confusión
matriz_confusion = confusion_matrix(y_heldout, y_pred)
sns.heatmap(matriz_confusion, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicción')
plt.ylabel('Real')
plt.title('Matriz de Confusión')
plt.show()
#%% GRAFICO EL ARBOL 
plt.figure(figsize=(50, 20))  
tree.plot_tree(arbol_elegido, filled=True, 
    feature_names=[f"pixel_{i}" for i in range(X_dev.shape[1])],
    class_names=[str(i) for i in range(10)], fontsize=10, max_depth=3)
plt.title("Primeros 3 niveles del arbol de decision final")
plt.show()

#%% 
