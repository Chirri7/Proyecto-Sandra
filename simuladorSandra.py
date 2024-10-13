import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox

# Constante de Coulomb
k_e = 8.99e9  # N·m^2/C^2

# Definir las propiedades iniciales de las cargas
cargas = []  # Lista de cargas
pos_cargas = []  # Lista de posiciones de las cargas

# Inicializar variable para seguimiento de la carga arrastrada
arrastrando = None
strm = None  # Variable para mantener el streamplot
colorbar = None  # Variable para la barra de color

# Función para calcular el campo eléctrico en un punto debido a una carga puntual
def campo_electrico(q, pos_carga, pos_punto):
    r_vec = np.array(pos_punto) - np.array(pos_carga)  # Vector de la carga al punto
    r_mag = np.linalg.norm(r_vec)  # Magnitud de la distancia
    if r_mag == 0:  # Evitar división por cero
        return np.array([0, 0])
    # Campo eléctrico en función de la distancia y magnitud de la carga
    E_vec = k_e * q / r_mag**2 * (r_vec / r_mag)  # Normalizar el vector de posición
    return E_vec

# Función para actualizar la visualización del campo eléctrico
def actualizar_campo():
    global strm, colorbar
    x = np.linspace(-0.5, 0.5, 50)  # Crear cuadrícula de puntos en x
    y = np.linspace(-0.5, 0.5, 50)  # Crear cuadrícula de puntos en y
    X, Y = np.meshgrid(x, y)
    puntos = np.vstack([X.ravel(), Y.ravel()]).T  # Combinar xey en puntos

    # Calcular el campo eléctrico en cada punto de la cuadrícula
    E_total = np.zeros((len(puntos), 2))
    for i, punto in enumerate(puntos):
        for q, pos_carga in zip(cargas, pos_cargas):
            E_total[i] += campo_electrico(q, pos_carga, punto)

    # Redimensionar para visualización
    Ex = E_total[:, 0].reshape(X.shape)
    Ey = E_total[:, 1].reshape(X.shape)

    # Limpiar la figura, pero no los botones ni el diseño
    ax.clear()

    # Crear el gráfico del campo eléctrico usando streamplot
    strm = ax.streamplot(X, Y, Ex, Ey, color=np.log(np.sqrt(Ex**2 + Ey**2) + 1e-10), cmap='cool', density=2)

    # Solo agregar la barra de color una vez
    if colorbar is None:
        colorbar = plt.colorbar(strm.lines, ax=ax)
    
    # Dibujar las cargas como círculos (esferas)
    for i, (pos, q) in enumerate(zip(pos_cargas, cargas)):
        color = 'red' if q > 0 else 'blue'  # Color basado en la carga
        ax.scatter(pos[0], pos[1], color=color, s=1000, zorder=5, marker='o')  # Dibujar la carga como un círculo grande
        ax.annotate(f'{q:.1e} C', (pos[0], pos[1]), textcoords="offset points", xytext=(0, 10), ha='center', color=color)

    # Fijar los límites de los ejes para que no cambien al actualizar
    ax.set_xlim(-0.5, 0.5)
    ax.set_ylim(-0.5, 0.5)
    ax.set_title("Campo Eléctrico: Haga clic y arrastre las cargas")
    ax.grid(False)
    plt.draw()  # Actualizar la visualización

# Función para agregar carga a la lista
def agregar_carga(q):
    global pos_cargas
    pos_cargas.append([0.0, 0.0])  # Agregar carga en la posición (0, 0)
    cargas.append(q)  # Añadir la carga a la lista
    actualizar_campo()  # Actualizar el campo después de agregar

# Función para manejar eventos de clic del mouse
def on_click(event):
    global arrastrando
    # Determinar si se hizo clic cerca de alguna carga
    if event.inaxes != ax:
        return
    for i, pos in enumerate(pos_cargas):
        if np.hypot(event.xdata - pos[0], event.ydata - pos[1]) < 0.05:  # Tolerancia para seleccionar la carga
            arrastrando = i  # Guardar índice de la carga que está siendo arrastrada
            break

# Función para manejar eventos de movimiento del mouse
def on_move(event):
    global arrastrando
    if arrastrando is not None and event.inaxes == ax:  # Actualizar la posición de la carga seleccionada
        pos_cargas[arrastrando] = [event.xdata, event.ydata]
        actualizar_campo()  # Redibujar el campo eléctrico

# Función para manejar cuando se suelta el clic del mouse
def on_release(event):
    global arrastrando
    arrastrando = None  # Dejar de arrastrar la carga

# Función para agregar carga basada en el valor ingresado
def agregar_carga_con_valor(event):
    try:
        q = float(textbox_valor.text)  # Obtener el valor de la caja de texto
        agregar_carga(q)  # Agregar la carga
        textbox_valor.set_val('')  # Limpiar el cuadro de texto después de agregar
    except ValueError:
        print("Valor no válido. Por favor ingrese un número.")

# Función para eliminar la última carga añadida
def eliminar_carga(event):
    global cargas, pos_cargas
    if cargas:  # Solo eliminar si hay cargas
        cargas.pop()  # Eliminar la última carga de la lista
        pos_cargas.pop()  # Eliminar la posición correspondiente
        actualizar_campo()  # Actualizar el campo después de eliminar

# Función para calcular el campo eléctrico total y mostrar en la interfaz
def calcular_campo_total(event):
    if cargas:
        campo_total = np.zeros(2)
        for q, pos_carga in zip(cargas, pos_cargas):
            campo_total += campo_electrico(q, pos_carga, [0, 0])  # Calcular en (0, 0)
        textbox_respuesta.set_val(f'Campo Total: {campo_total[0]:.2e} N/C, {campo_total[1]:.2e} N/C')

# Configuración de la figura y conexión de los eventos
fig, ax = plt.subplots(figsize=(10, 6))

# Agregar un título para la interfaz
plt.text(0.5, 1.05, "Simulador de campo eléctrico", fontsize=14, ha='center')

# Agregar una caja de texto para el valor de la carga
textbox_valor = TextBox(plt.axes([0.55, 0.8, 0.25, 0.05]), '')  # Caja de texto sin etiqueta
plt.text(0.2, 1.2, 'Valor de la Carga (C):', fontsize=10, ha='left')  # Etiqueta independiente

# Fijar los botones en áreas específicas que no interfieran con el área de gráficos
btn_agregar = Button(plt.axes([0.55, 0.7, 0.25, 0.05]), 'Agregar Carga')  # Posición y tamaño del botón
btn_agregar.on_clicked(agregar_carga_con_valor)  # Conectar el botón a la función de agregar carga con valor

# Agregar un botón para eliminar cargas
btn_eliminar = Button(plt.axes([0.55, 0.6, 0.25, 0.05]), 'Eliminar Carga')  # Posición y tamaño del botón
btn_eliminar.on_clicked(eliminar_carga)  # Conectar el botón a la función de eliminar carga
plt.text(0.38, -1.2, 'Electra (IA):', fontsize=15, ha='left')  # Etiqueta independiente

# Agregar un botón para calcular el campo total
btn_calcular = Button(plt.axes([0.55, 0.4, 0.25, 0.05]), 'Calcular Campo')  # Posición y tamaño del botón
btn_calcular.on_clicked(calcular_campo_total)  # Conectar el botón a la función de calcular campo total

# Agregar una caja de texto para mostrar la respuesta del cálculo
textbox_respuesta = TextBox(plt.axes([0.55, 0.3, 0.25, 0.05]), '')  # Aquí no se necesita 'label' ni 'color'

# Conectar los eventos del mouse
fig.canvas.mpl_connect('button_press_event', on_click)
fig.canvas.mpl_connect('motion_notify_event', on_move)
fig.canvas.mpl_connect('button_release_event', on_release)

# Configuración inicial
plt.subplots_adjust(left=0.05, right=0.55, top=0.9, bottom=0.1)
ax.set_title("Campo Eléctrico: Haga clic y arrastre las cargas")
ax.grid(False)
actualizar_campo()  # Inicializar visualización

# Mostrar la figura
plt.show()
