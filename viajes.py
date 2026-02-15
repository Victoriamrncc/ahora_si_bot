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
            categoria = 'bajo'
            explicacion = f"Como el gasto diario por persona (${gasto_diario_pp:,.0f}) es menor a $50.000."
        
        elif gasto_diario_pp <= 100000:
            categoria = 'medio'
            explicacion = f"Como el gasto diario por persona (${gasto_diario_pp:,.0f}) está entre $50.000 y $100.000."
        
        else:
            categoria = 'alto'
            explicacion = f"Como el gasto diario por persona (${gasto_diario_pp:,.0f}) es mayor a $100.000."

        return categoria, gasto_diario_pp, explicacion

    except ZeroDivisionError:
        return 'bajo', 0, "No se pudo calcular correctamente el presupuesto."



sg.theme('GreenMono')

layout = [
    [sg.Text('Sistema Experto: Viajes Argentina', font=("Helvetica", 20))],
    [sg.HorizontalSeparator()],
    
    # Módulo de apoyo para el hecho 'Presupuesto'
    [sg.Frame('1. Calculadora de Presupuesto', [
        [sg.Text('Monto Total ($):'), sg.Input(key='-MONTO-', size=(10, 1)),
         sg.Text('Días:'), sg.Input(key='-DIAS-', size=(5, 1)),
         sg.Text('Personas:'), sg.Input(key='-PERSONAS-', size=(5, 1))],
        [sg.Button('Calcular Nivel')]
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
    [sg.Image(key='-IMAGE-', size=(300, 200))]
]

window = sg.Window('Argentina Travel Expert System', layout, finalize=True)

while True:
    event, values = window.read()
    
    if event in (sg.WIN_CLOSED, 'Salir'):
        break
    
    # Módulo de apoyo: Calculadora para determinar el nivel de presupuesto
    if event == 'Calcular Nivel':
        try:
            m, d, p = float(values['-MONTO-']), int(values['-DIAS-']), int(values['-PERSONAS-'])
            cat, gasto, explicacion = calcular_categoria_presupuesto(m, d, p)
            window['-PRES-'].update(value=cat)

            sg.popup(
                f"Tu gasto diario por persona es: ${gasto:,.0f}\n\n"
                f"{explicacion}\n\n"
                f"Nivel detectado: {cat.upper()}"
            )
        except ValueError:
            sg.popup_error("Ingresa números válidos en la calculadora.")

    # Módulo de Inferencia Principal
    if event == 'Consultar Destino':
        t, p, c = values['-TEMP-'], values['-PRES-'], values['-COMP-']
        
        # Extracción de evidencia de la interfaz (Mapeo de respuestas si/no)
        v_aven = 'si' if values['-AVEN_SI-'] else 'no'
        v_expl = 'si' if values['-EXPL_SI-'] else 'no'
        v_desc = 'si' if values['-DESC_SI-'] else 'no'

        if not all([t, p, c]):
            sg.popup_error('Por favor, selecciona temporada, presupuesto y compañía en la sección 3.')
            continue

        # PASO 1: Inferencia de Perfiles Acumulativos
        # Gracias a que eliminamos el 'corte' (!) en Prolog, esta consulta devuelve 
        # todos los perfiles que coincidan con los "si" del usuario.
        perfil_query = f"determinar_perfil(Perfil, {v_aven}, {v_expl}, {v_desc})"
        perfiles_detectados = list(prolog.query(perfil_query))
        
        if perfiles_detectados:
            window['-OUTPUT-'].update("") # Limpiar pantalla para nuevos resultados
            destinos_vistos = set() # Estructura para evitar duplicados en la visualización
            encontrado_al_menos_uno = False

            # PASO 2: El experto recorre cada perfil descubierto para dar recomendaciones
            for p_res in perfiles_detectados:
                per_final = p_res['Perfil']
                
                # Inferencia de Destinos por cada perfil hallado
                query_str = f"buscar_coincidencias(D, {t}, {p}, {c}, {per_final}, A), locacion(D, Prov, Reg)"
                resultados = list(prolog.query(query_str))
                
                if resultados:
                    encontrado_al_menos_uno = True
                    window['-OUTPUT-'].update(f"--- RECOMENDACIONES PARA PERFIL {per_final.upper()} ---\n", append=True)
                    
                    for res in resultados:
                        # Solo procesamos si no mostramos este destino antes en otro perfil
                        if res['D'] not in destinos_vistos:
                            nombre = str(res['D']).replace('_', ' ').capitalize()
                            prov = str(res['Prov']).replace('_', ' ').capitalize()
                            reg = str(res['Reg']).replace('_', ' ').capitalize()
                            act = str(res['A']).replace('_', ' ').capitalize()
                            
                            info = (f"DESTINO: {nombre}\n"
                                    f"UBICACIÓN: Prov. de {prov} ({reg})\n"
                                    f"ACTIVIDAD RECOMENDADA: {act}\n"
                                    f"{'-'*30}\n")
                            window['-OUTPUT-'].update(info, append=True)
                            
                            destinos_vistos.add(res['D'])
                            
                            # Actualizar imagen con el primer destino encontrado
                            img_path = f"img/{res['D']}.png"
                            if os.path.exists(img_path):
                                window['-IMAGE-'].update(filename=img_path)

            if not encontrado_al_menos_uno:
                window['-OUTPUT-'].update("No encontramos destinos que coincidan con todos tus filtros.")
                window['-IMAGE-'].update(data=None)
        else:
            window['-OUTPUT-'].update("No se pudo determinar un perfil de viajero.")

window.close()
