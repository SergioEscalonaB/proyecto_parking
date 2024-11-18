import cv2
import numpy as np

# Lista de posiciones de los lugares de estacionamiento
posList = [
    (1, [(55, 100), (140, 98), (164, 146), (41, 146)])
]

cap = cv2.VideoCapture('CarPark.mp4')

def checkParkingSpace(imgPro, img, posList):
    contadorEspacios = 0

    for i, pos in enumerate(posList):
        points = np.array(pos[1], np.int32)
        points = points.reshape((-1, 1, 2))
        rect = cv2.boundingRect(points)
        x, y, w, h = rect
        text_size = cv2.getTextSize(str(i+1), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        text_x = x + (w - text_size[0]) // 2
        text_y = y + (h + text_size[1]) // 2
        cv2.putText(img, str(i+1), (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    for pos in posList:
        points = np.array(pos[1], np.int32)
        points = points.reshape((-1, 1, 2))
        rect = cv2.boundingRect(points)
        x, y, w, h = rect
        imgCrop = imgPro[y:y + h, x:x + w]  # Extraer cada espacio de estacionamiento

        count = cv2.countNonZero(imgCrop)  # Contar píxeles no cero

        if count < 800:  # Umbral ajustable
            color = (0, 255, 0)  # Verde para espacios vacíos
            thickness = 2
            contadorEspacios += 1
        else:
            color = (0, 0, 255)  # Rojo para espacios ocupados
            thickness = 2

        # Dibujar rectángulo y conteo
        cv2.polylines(img, [points], True, color, thickness)
        cv2.putText(img, str(count), (x, y + h - 3), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2) # Muestra en el cuadro el umbral
    # Mostrar el número total de espacios libres
    cv2.putText(img, f"Libres: {contadorEspacios}/{len(posList)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 0), 2)

while True:
    success, img = cap.read()
    if not success:
        print("No se puede recibir más frames. Saliendo...")
        break

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convertir a escala de grises
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)  # Aplicar desenfoque
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 17, 20)  # Modificar color BN
    imgMedian = cv2.medianBlur(imgThreshold, 5)  # Elimina ruido y sal 
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgThreshold, kernel, iterations=1)  # Más delgados los píxeles
    cv2.imshow("Imagen a procesar: ", imgDilate)

    # Verificación de los espacios de parking
    checkParkingSpace(imgDilate, img, posList)
    cv2.imshow("Detección de espacios libres de Parking", img)  # Mostrar imagen
    if cv2.waitKey(50) & 0xFF == ord('q'):  # Salir con la tecla 'q'
        break

cap.release()
cv2.destroyAllWindows()




