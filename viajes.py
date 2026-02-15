import PySimpleGUI as sg
from pyswip import Prolog
import os

# Inicializar Prolog
prolog = Prolog()
prolog.consult("viajes.pl")

def obtener_lista(predicado):
    """Extrae listas de opciones desde Prolog (temporadas, presupuestos, etc.)"""
    try:
        res = list(prolog.query(f"{predicado}(L)"))
        return res[0]['L'] if res else []
    except:
        return []
    
def calcular_categoria_presupuesto(monto, dias, personas):
    """Calcula la categoría basada en el gasto diario por persona"""
    try:
        gasto_diario_pp = monto / (dias * personas)
        if gasto_diario_pp < 50000:
            return 'bajo'
        elif 50000 <= gasto_diario_pp <= 100000:
            return 'medio'
        else:
            return 'alto'
    except ZeroDivisionError:
        return 'bajo'
    

# --- CARGA DINÁMICA ---
destinos_db = obtener_lista('lista_destinos')
sg.theme('GreenMono')

# --- ESTILOS REUTILIZABLES ---
label_sz = (15, 1)

layout_experto = [
    [sg.Push(), sg.Text('Sistema Experto: Viajes Argentina', font=("Helvetica", 22, "bold")), sg.Push()],
    [sg.HorizontalSeparator(pad=(0, 10))],
    
    [sg.Column([
        # Sección 1: Presupuesto
        [sg.Frame('1. Calculadora de Presupuesto', [
            [sg.Text('Monto Total ($):', size=(12, 1)), sg.Input(key='-MONTO-', size=(10, 1)),
             sg.Text('Días:'), sg.Input(key='-DIAS-', size=(5, 1)),
             sg.Text('Personas:'), sg.Input(key='-PERSONAS-', size=(5, 1))],
            [sg.Button('Calcular Presupuesto', size=(18, 1), pad=(5, 10))]
        ], p=10, expand_x=True)],

        # Sección 2: Intereses
        [sg.Frame('2. Perfil de Viaje (Intereses)', [
            [sg.Text('¿Aventura y adrenalina?', size=(25, 1)), 
             sg.Radio('Sí', "R1", key='-AVEN_SI-'), sg.Radio('No', "R1", default=True, key='-AVEN_NO-')],
            [sg.Text('¿Museos y cultura?', size=(25, 1)), 
             sg.Radio('Sí', "R2", key='-EXPL_SI-'), sg.Radio('No', "R2", default=True, key='-EXPL_NO-')],
            [sg.Text('¿Tranquilidad y relax?', size=(25, 1)), 
             sg.Radio('Sí', "R3", key='-DESC_SI-'), sg.Radio('No', "R3", default=True, key='-DESC_NO-')]
        ], p=10, expand_x=True)],

        # Sección 3: Detalles
        [sg.Frame('3. Detalles Generales', [
            [sg.Text('Temporada:', size=label_sz), sg.Combo(obtener_lista('lista_temporadas'), key='-TEMP-', readonly=True, expand_x=True)],
            [sg.Text('Presupuesto:', size=label_sz), sg.Combo(obtener_lista('lista_presupuestos'), key='-PRES-', readonly=True, expand_x=True)],
            [sg.Text('Compañía:', size=label_sz), sg.Combo(obtener_lista('lista_companias'), key='-COMP-', readonly=True, expand_x=True)]
        ], p=10, expand_x=True)],
        
        [sg.Button('Consultar Destino', size=(25, 1), button_color=('white', '#2c3e50'), font=('Helvetica', 10, 'bold')), 
         sg.Button('Salir', size=(10, 1))]
    ], p=0), 
    
    # Columna Derecha: Resultados e Imagen
    sg.Column([
        [sg.Text('Inferencia del Sistema:', font=("Helvetica", 12, 'bold'))],
        [sg.Multiline(size=(50, 8), key='-OUTPUT-', font=("Consolas", 10), background_color='#f0f0f0')],
        [sg.Frame('Vista del Destino', [[sg.Image(key='-IMAGE-', size=(350, 180), background_color='white')]], p=5)]
    ], vertical_alignment='top')]
]

# Pestaña 2: TSP con mejor scroll
layout_viajante = [
    [sg.Text('Optimización de Ruta (TSP)', font=("Helvetica", 18, "bold"), pad=(0, 10))],
    [sg.Frame('Seleccioná tus destinos de interés', [
        [sg.Column([[sg.Checkbox(d.replace('_', ' ').capitalize(), key=f'-CB_{d}-', pad=(5, 5))] for d in destinos_db], 
                   scrollable=True, vertical_scroll_only=True, size=(500, 250), background_color='#e8e8e8')]
    ], p=10)],
    [sg.Button('Calcular Ruta Óptima', size=(20, 1), button_color='firebrick')],
    [sg.Text('Resultado:', font=("Helvetica", 11, 'bold'))],
    [sg.Multiline(size=(65, 5), key='-OUT_TSP-', disabled=True, font=("Consolas", 11))]
]

# Layout Final con TabGroup expandido
layout = [
    [sg.TabGroup([[
        sg.Tab(' Sistema Experto', layout_experto),
        sg.Tab(' Optimización de Ruta (TSP)', layout_viajante)
    ]], expand_x=True, expand_y=True, tab_location='topleft')],
    [sg.Sizegrip()] # Para que puedas redimensionar la ventana
]

window = sg.Window('Final Algorítmica - UCA', layout, resizable=True, finalize=True)

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Salir'): 
        break

    if event == 'Calcular Nivel': # Ajustado al nombre de tu botón
        try:
            m, d, p = float(values['-MONTO-']), int(values['-DIAS-']), int(values['-PERSONAS-'])
            # Usamos tu función de cálculo que devuelve la categoría y la explicación
            cat, gasto, explicacion = calcular_categoria_presupuesto(m, d, p) 
            window['-PRES-'].update(value=cat)
            sg.popup(f"Presupuesto detectado: {cat.upper()}\n\n{explicacion}")
        except ValueError: 
            sg.popup_error("Ingresa números válidos.")

    if event == 'Consultar Destino':
        t, p, c = values['-TEMP-'], values['-PRES-'], values['-COMP-']
        v_aven = 'si' if values['-AVEN_SI-'] else 'no'
        v_expl = 'si' if values['-EXPL_SI-'] else 'no'
        v_desc = 'si' if values['-DESC_SI-'] else 'no'

        if not all([t, p, c]):
            sg.popup_error('Completa los campos de la sección 3.')
            continue

        perfiles = list(prolog.query(f"determinar_perfil(Perfil, {v_aven}, {v_expl}, {v_desc})"))
        
        if perfiles:
            window['-OUTPUT-'].update("SISTEMA EXPERTO: RAZONAMIENTO LOGICO\n" + "="*40 + "\n")
            vistos = set()
            encontrado = False

            for per in perfiles:
                # Mantenemos tu consulta detallada
                q = f"buscar_coincidencias_detallada(D, {t}, {p}, {c}, {per['Perfil']}, Act, Expl)"
                
                for res in list(prolog.query(q)):
                    if res['D'] not in vistos:
                        encontrado = True
                        # 1. Mostrar la explicación en el Multiline
                        explicacion = res['Expl'].decode('utf-8') if isinstance(res['Expl'], bytes) else res['Expl']
                        window['-OUTPUT-'].update(f"• {explicacion}\n\n", append=True)
                        
                        # 2. ACTUALIZAR LA IMAGEN (Esta es la parte clave)
                        # Busca el archivo en la carpeta img/ con el nombre del átomo de Prolog (ej: bariloche.png)
                        img_path = f"img/{res['D']}.png"
                        if os.path.exists(img_path):
                            window['-IMAGE-'].update(filename=img_path)
                        
                        vistos.add(res['D'])
            
            if not encontrado:
                window['-OUTPUT-'].update("No hay destinos que coincidan con todos tus filtros.")
                window['-IMAGE-'].update(data=None) # Limpia la imagen si no hay resultados
        else:
            window['-OUTPUT-'].update("No se pudo determinar un perfil de usuario.")
            window['-IMAGE-'].update(data=None)
    if event == 'Calcular Ruta Óptima':
        seleccionados = [d for d in destinos_db if values.get(f'-CB_{d}-')]
        if len(seleccionados) < 2:
            sg.popup_error("Elegí al menos 2 ciudades.")
            continue
        
        lista_p = "[" + ",".join(seleccionados) + "]"
        try:
            res = list(prolog.query(f"mejor_ruta({lista_p}, Ruta, Dist)"))
            if res:
                sol = res[0]
                txt = " → ".join([str(c).capitalize() for c in sol['Ruta']])
                window['-OUT_TSP-'].update(f"RUTA: {txt}\nDISTANCIA: {sol['Dist']} km")
            else:
                window['-OUT_TSP-'].update("No se encontró una ruta continua.")
        except Exception as e:
            sg.popup_error(f"Error lógico: {e}")

window.close()