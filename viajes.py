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
    [sg.Text('Sistema Experto: Viajes Argentina', font=("Helvetica", 20))],
    [sg.HorizontalSeparator()],
    
    # Módulo de apoyo para el hecho 'Presupuesto'
    [sg.Frame('1. Calculadora de Presupuesto', [
        [sg.Text('Monto Total ($):'), sg.Input(key='-MONTO-', size=(10, 1)),
         sg.Text('Días:'), sg.Input(key='-DIAS-', size=(5, 1)),
         sg.Text('Personas:'), sg.Input(key='-PERSONAS-', size=(5, 1))],
        [sg.Button('Calcular Presupuesto')]
    ])],

    # Interfaz para el descubrimiento de Perfil (Extracción de Evidencia)
    [sg.Frame('2. Perfil de Viaje (Intereses)', [
        [sg.Text('¿Te atrae la aventura física y adrenalina?'), 
         sg.Radio('Sí', "R1", key='-AVEN_SI-'), sg.Radio('No', "R1", default=True, key='-AVEN_NO-')],
        [sg.Text('¿Disfrutas de museos, historia y cultura?'), 
         sg.Radio('Sí', "R2", key='-EXPL_SI-'), sg.Radio('No', "R2", default=True, key='-EXPL_NO-')],
        [sg.Text('¿Buscas tranquilidad y paisajes relax?'), 
         sg.Radio('Sí', "R3", key='-DESC_SI-'), sg.Radio('No', "R3", default=True, key='-DESC_NO-')]
    ])],

    # Selectores de Hechos Categóricos
    [sg.Frame('3. Detalles Generales', [
        [sg.Text('Temporada:', size=(10, 1)), sg.Combo(obtener_lista('lista_temporadas'), key='-TEMP-', readonly=True, expand_x=True)],
        [sg.Text('Presupuesto:', size=(10, 1)), sg.Combo(obtener_lista('lista_presupuestos'), key='-PRES-', readonly=True, expand_x=True)],
        [sg.Text('Compañía:', size=(10, 1)), sg.Combo(obtener_lista('lista_companias'), key='-COMP-', readonly=True, expand_x=True)]
    ])],
    
    [sg.Button('Consultar Destino', size=(20, 1)), sg.Button('Salir')],
    [sg.HorizontalSeparator()],
    [sg.Text('Inferencia del Sistema Experto:', font=("Helvetica", 12, 'bold'))],
    [sg.Multiline(size=(60, 10), key='-OUTPUT-', font=("Consolas", 10))],
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

layout_mt = [
    [sg.Text('Simulador de Máquina de Turing: Validador de Tickets', font=("Helvetica", 16))],
    [sg.Frame('Requisitos del Ticket', [
        [sg.Text('Formato requerido: 3 Letras + 4 Números (Ej: ARG2026)')],
        [sg.Input(key='-TICKET_IN-', size=(20, 1)), 
         sg.Button('Validar con MT', button_color='seagreen')]
    ])],
    [sg.Text('Salida de la Unidad de Control:', font=("Helvetica", 11, 'bold'))],
    [sg.Multiline(size=(65, 6), key='-OUT_MT-', font=("Consolas", 11), 
                  text_color='lime', background_color='black', disabled=True)]
]

# Layout Final con TabGroup expandido
layout = [
    [sg.TabGroup([[
        sg.Tab(' Sistema Experto', layout_experto),
        sg.Tab(' Optimización (TSP)', layout_viajante),
        sg.Tab(' Validación (MT)', layout_mt) # Nueva pestaña
    ]], expand_x=True, expand_y=True)]
]

window = sg.Window('Final Algorítmica - UCA', layout, resizable=True, finalize=True)

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Salir'): break

    if event == 'Calcular Presupuesto':
        try:
            m, d, p = float(values['-MONTO-']), int(values['-DIAS-']), int(values['-PERSONAS-'])
            cat = calcular_categoria_presupuesto(m, d, p)
            window['-PRES-'].update(value=cat)
            sg.popup(f"Presupuesto detectado: {cat.upper()}")
        except ValueError: sg.popup_error("Ingresa números válidos.")

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
            window['-OUTPUT-'].update("SISTEMA EXPERTO: RAZONAMIENTO LOGICO\n" + "="*40 + "\n") # NUEVO: Encabezado
            vistos = set()
            for per in perfiles:
                # NUEVO: Llamamos a 'buscar_coincidencias_detallada' que creamos en el .pl
                q = f"buscar_coincidencias_detallada(D, {t}, {p}, {c}, {per['Perfil']}, Act, Expl)"
                
                for res in list(prolog.query(q)):
                    if res['D'] not in vistos:
                        # NUEVO: En lugar de imprimir solo el destino, imprimimos la explicación 'Expl'
                        explicacion = res['Expl'].decode('utf-8') if isinstance(res['Expl'], bytes) else res['Expl']
                        window['-OUTPUT-'].update(f"• {explicacion}\n\n", append=True)
                        vistos.add(res['D'])

            if not vistos:
                mensaje_vacio = "Lo sentimos, nuestra base de datos no encontró una recomendación para estas características."
                window['-OUTPUT-'].update(f"\n{mensaje_vacio}", append=True)
            # -----------------------------
        else:
            window['-OUTPUT-'].update("No se pudo determinar un perfil de usuario.")

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

    if event == 'Validar con MT':
        ticket = values['-TICKET_IN-'].strip()
        if len(ticket) != 7:
            sg.popup_error("El ticket debe tener exactamente 7 caracteres.")
            continue
            
        try:
            res = list(prolog.query(f"validar_ticket('{ticket}', Res)"))
            if res:
                resultado = res[0]['Res']
                # Decodificar si es necesario
                msg = resultado.decode('utf-8') if isinstance(resultado, bytes) else resultado
                window['-OUT_MT-'].update(f"CINTA: [ {ticket} | B ]\n" + "-"*30 + f"\nLOG: Analizando secuencia de entrada...\nRESULTADO: {msg}")
            else:
                window['-OUT_MT-'].update(f"CINTA: [ {ticket} | B ]\n" + "-"*30 + "\nLOG: La MT se detuvo en un estado de rechazo.\nRESULTADO: Ticket INVALIDO")
        except Exception as e:
            sg.popup_error(f"Error en el motor logico: {e}")

window.close()