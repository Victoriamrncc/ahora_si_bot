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

sg.theme('GreenMono')

sg.theme('GreenMono')

layout = [
    [sg.Text('Sistema Experto: Viajes Argentina', font=("Helvetica", 20))],
    [sg.HorizontalSeparator()],
    
    # Sección de Calculadora de Presupuesto
    [sg.Frame('Calculadora de Presupuesto', [
        [sg.Text('Monto Total ($):', size=(15, 1)), sg.Input(key='-MONTO-', size=(10, 1)),
         sg.Text('Días:', size=(5, 1)), sg.Input(key='-DIAS-', size=(5, 1)),
         sg.Text('Personas:', size=(8, 1)), sg.Input(key='-PERSONAS-', size=(5, 1))],
        [sg.Button('Calcular Categoría', size=(15, 1))]
    ])],

    [sg.HorizontalSeparator()],
    
    # Selectores
    [sg.Text('Temporada:', size=(12, 1)),
     sg.Combo(obtener_lista('lista_temporadas'), key='-TEMP-', readonly=True, expand_x=True)],

    [sg.Text('Presupuesto:', size=(12, 1)),
     sg.Combo(obtener_lista('lista_presupuestos'), key='-PRES-', readonly=True, expand_x=True)],

    [sg.Text('Compañía:', size=(12, 1)),
     sg.Combo(obtener_lista('lista_companias'), key='-COMP-', readonly=True, expand_x=True)],
    
    [sg.Button('Consultar Destino', size=(20, 1)), sg.Button('Salir')],
    
    [sg.HorizontalSeparator()],
    [sg.Text('Resultado de la Inferencia:', font=("Helvetica", 12, 'bold'))],
    [sg.Multiline(size=(50, 8), key='-OUTPUT-', font=("Consolas", 11))],
    [sg.Image(key='-IMAGE-', size=(300, 200))]
]

window = sg.Window('Argentina Travel Expert System', layout, finalize=True)

while True:
    event, values = window.read()
    
    if event in (sg.WIN_CLOSED, 'Salir'):
        break
    
    # Lógica de la calculadora
    if event == 'Calcular Categoría':
        try:
            m = float(values['-MONTO-'])
            d = int(values['-DIAS-'])
            p = int(values['-PERSONAS-'])
            
            categoria = calcular_categoria_presupuesto(m, d, p)
            window['-PRES-'].update(value=categoria)
            sg.popup(f"Basado en tu gasto diario, tu presupuesto es: {categoria.upper()}")
        except ValueError:
            sg.popup_error("Por favor, ingresa números válidos en la calculadora.")

    if event == 'Consultar Destino':
        t, p, c = values['-TEMP-'], values['-PRES-'], values['-COMP-']
        
        if not all([t, p, c]):
            sg.popup_quick_message('Selecciona todas las opciones', background_color='red')
            continue

        query_str = f"recomendar_destino(D, {t}, {p}, {c}, A), locacion(D, Prov, Reg)"
        resultados = list(prolog.query(query_str))
        
        if resultados:
            window['-OUTPUT-'].update("")
            for res in resultados:
                nombre = str(res['D']).replace('_', ' ').capitalize()
                prov = str(res['Prov']).replace('_', ' ').capitalize()
                reg = str(res['Reg']).replace('_', ' ').capitalize()
                act = str(res['A']).replace('_', ' ').capitalize()
                
                info = (f"DESTINO: {nombre}\n"
                        f"UBICACIÓN: Prov. de {prov} ({reg})\n"
                        f"ACTIVIDAD SUGERIDA: {act}\n"
                        f"{'-'*30}\n")
                
                window['-OUTPUT-'].update(info, append=True)
                
                img_path = f"img/{res['D']}.png"
                if os.path.exists(img_path):
                    window['-IMAGE-'].update(filename=img_path)
                else:
                    window['-IMAGE-'].update(data=None)
        else:
            window['-OUTPUT-'].update("No hay destinos que coincidan con todos los filtros.")
            window['-IMAGE-'].update(data=None)

window.close()