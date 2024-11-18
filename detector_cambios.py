import cv2
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json

# Inicializa Firebase con tu clave de servicio
cred = credentials.Certificate('C:\\Users\\sergi\\Desktop\\parking-66bb4-firebase-adminsdk-5x5f0-810cb338ec.json')  # Reemplaza con la ruta correcta
firebase_admin.initialize_app(cred)
db = firestore.client()

# Cargar la base de datos local desde un archivo JSON
def cargar_base_datos_local():
    with open('db_local.json', 'r') as file:
        return json.load(file)

# Guardar los cambios en la base de datos local
def guardar_base_datos_local(estado_local):
    with open('db_local.json', 'w') as file:
        json.dump(estado_local, file)

# Inicializar la base de datos local y Firebase con todos los lugares en estado "ROJO"
def inicializar_estados_a_rojo():
    global estado_local
    for identificador in estado_local:
        estado_local[identificador] = "ROJO"
        # Solo actualizar el estado en Firebase, pero no incrementar el contador
        cambiar_estado_en_firebase_sin_incrementar(identificador, "ROJO")  # Nueva función sin incremento
    guardar_base_datos_local(estado_local)  # Guardar el cambio en la base de datos local
    print("Todos los lugares se han inicializado a ROJO.")

def cambiar_estado_en_firebase_sin_incrementar(identificador, nuevo_estado):
    doc_ref = db.collection(u'lugares').document(str(identificador))
    doc_ref.update({
        u'estado': nuevo_estado
    })


# Inicializar el contador en Firebase
def inicializar_contador():
    doc_ref = db.collection(u'lugares').document(u'999')
    doc_ref.set({
        u'contador': 1
    })

# Incrementar el contador en Firebase
def incrementar_contador():
    doc_ref = db.collection(u'lugares').document(u'999')
    doc_ref.update({
        u'contador': firestore.Increment(1)
    })

# Actualizar en Firebase solo si el estado ha cambiado
def cambiar_estado_en_firebase(identificador, nuevo_estado):
    doc_ref = db.collection(u'lugares').document(str(identificador))
    doc_ref.update({
        u'estado': nuevo_estado
    })
    incrementar_contador()  # Incrementar el contador cada vez que se actualiza un estado

# Cambiar estado solo si es diferente al estado local
def cambiar_estado_si_necesario(identificador, nuevo_estado):
    global estado_local
    if estado_local[str(identificador)] != nuevo_estado:
        # Actualizar en Firebase y también localmente
        cambiar_estado_en_firebase(identificador, nuevo_estado)
        estado_local[str(identificador)] = nuevo_estado
        guardar_base_datos_local(estado_local)  # Guardar el cambio en la base de datos local
        print(f"Actualizado el lugar {identificador} a {nuevo_estado}")
    else:
        print(f"Lugar {identificador} no cambió, no se actualiza.")

# Lista de posiciones de los lugares de estacionamiento
posList = [
    (1, 55, 100), (2, 163, 98), (3, 56, 146), (4, 164, 146),
    (5, 50, 193), (6, 158, 194), (7, 50, 241), (8, 159, 242),
    (9, 53, 289), (10, 161, 290), (11, 54, 337), (12, 161, 339),
    (13, 50, 384), (14, 160, 387), (15, 51, 431), (16, 162, 429),
    (17, 52, 479), (18, 162, 478), (19, 52, 527), (20, 167, 525),
    (21, 50, 573), (22, 167, 573), (23, 56, 623), (24, 165, 619),
    (25, 406, 89), (26, 514, 92), (27, 402, 138), (28, 512, 138),
    (29, 404, 189), (30, 514, 187), (31, 401, 238), (32, 511, 236),
    (33, 401, 289), (34, 511, 284), (35, 402, 338), (36, 513, 329),
    (37, 404, 381), (38, 510, 380), (39, 405, 427), (40, 511, 426),
    (41, 406, 525), (42, 513, 524), (43, 402, 569), (44, 513, 568),
    (45, 407, 619), (46, 513, 619), (47, 755, 86), (48, 755, 136),
    (49, 901, 137), (50, 750, 188), (51, 900, 190), (52, 754, 232),
    (53, 901, 232), (54, 752, 276), (55, 895, 284), (56, 751, 327),
    (57, 897, 330), (58, 752, 377), (59, 898, 374), (60, 757, 426),
    (61, 901, 424), (62, 753, 472), (63, 903, 474), (64, 757, 518),
    (65, 899, 522), (66, 760, 573), (67, 900, 576), (68, 760, 616),
    (69, 900, 620)
]

cap = cv2.VideoCapture('CarPark.mp4')
width, height = 107, 48  # Dimensiones de cada espacio de estacionamiento

def checkParkingSpace(imgPro, img):
    global posList
    contadorEspacios = 0

    for i, pos in enumerate(posList):
        x, y = pos[1], pos[2]
        text_size = cv2.getTextSize(str(i+1), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        text_x = x + (width - text_size[0]) // 2
        text_y = y + (height + text_size[1]) // 2
        cv2.putText(img, str(i+1), (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    for pos in posList:
        x, y = pos[1], pos[2]
        imgCrop = imgPro[y:y + height, x:x + width]  # Extraer cada espacio de estacionamiento

        count = cv2.countNonZero(imgCrop)  # Contar píxeles no cero

        if count < 800:  # Umbral ajustable
            color = (0, 255, 0)  # Verde para espacios vacíos
            contadorEspacios += 1
            nuevo_estado = "VERDE"
        else:
            color = (0, 0, 255)  # Rojo para espacios ocupados
            nuevo_estado = "ROJO"
        
        identificador = pos[0]
        cambiar_estado_si_necesario(identificador, nuevo_estado)  # Solo actualizar si cambia el estado

        # Dibujar rectángulo y conteo
        cv2.rectangle(img, (x, y), (x + width, y + height), color, 2)
        cv2.putText(img, str(count), (x, y + height - 3), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    # Mostrar el número total de espacios libres
    cv2.putText(img, f"Libres: {contadorEspacios}/{len(posList)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 0), 2)

# Inicializar la base de datos local
estado_local = cargar_base_datos_local()

# Inicializar todos los estados a "ROJO" tanto localmente como en Firebase
inicializar_estados_a_rojo()

# Inicializar el contador en Firebase
inicializar_contador()

while True:
    success, img = cap.read()
    if not success:
        print("No se puede recibir más frames. Saliendo...")
        break

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convertir a escala de grises
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)  # Aplicar desenfoque
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 17, 20)
    imgMedian = cv2.medianBlur(imgThreshold, 5) # Elimina ruido y sal 
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgThreshold, kernel, iterations=1)
    cv2.imshow("Imagen a procesar: ", imgDilate)

    # Verificación de los espacios de parking
    checkParkingSpace(imgDilate, img)
    cv2.imshow("Detección de espacios libres de Parking", img)  # Mostrar imagen

    if cv2.waitKey(50) & 0xFF == ord('q'):  # Salir con la tecla 'q'
        break

cap.release()
cv2.destroyAllWindows()



