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

sg.theme('GreenMono')

layout = [
    [sg.Text('Sistema Experto: Viajes Argentina', font=("Helvetica", 20))],
    [sg.HorizontalSeparator()],
    
    # Selectores
    [sg.Text('Temporada:', size=(12, 1)),
     sg.Combo(obtener_lista('lista_temporadas'),
              key='-TEMP-', readonly=True, expand_x=True)],

    [sg.Text('Presupuesto:', size=(12, 1)),
     sg.Combo(obtener_lista('lista_presupuestos'),
              key='-PRES-', readonly=True, expand_x=True)],

    [sg.Text('Compañía:', size=(12, 1)),
     sg.Combo(obtener_lista('lista_companias'),
              key='-COMP-', readonly=True, expand_x=True)],
    
    [sg.Button('Consultar Destino', size=(20, 1)),
     sg.Button('Salir')],
    
    [sg.HorizontalSeparator()],
    [sg.Text('Resultado de la Inferencia:', font=("Helvetica", 12, 'bold'))],
    
    # Área resultado → sin colores hardcodeados
    [sg.Multiline(size=(50, 8),
                  key='-OUTPUT-',
                  font=("Consolas", 11))],
    
    # Imagen → sin background manual
    [sg.Image(key='-IMAGE-', size=(300, 200))]
]


window = sg.Window('Argentina Travel Expert System', layout, finalize=True)

while True:
    event, values = window.read()
    
    if event in (sg.WIN_CLOSED, 'Salir'):
        break
        
    if event == 'Consultar Destino':
        t, p, c = values['-TEMP-'], values['-PRES-'], values['-COMP-']
        
        if not all([t, p, c]):
            sg.popup_quick_message('Selecciona todas las opciones', background_color='red')
            continue

        # Usamos tu regla: recomendar_destino(Destino, Temp, Pres, Comp, Act)
        # También pedimos Provincia y Región para enriquecer la respuesta
        query_str = f"recomendar_destino(D, {t}, {p}, {c}, A), locacion(D, Prov, Reg)"
        resultados = list(prolog.query(query_str))
        
        if resultados:
            # Limpiar salida previa
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
                
                # Manejo de imagen seguro
                img_path = f"img/{res['D']}.png"
                if os.path.exists(img_path):
                    window['-IMAGE-'].update(filename=img_path)
                else:
                    window['-IMAGE-'].update(data=None) # Si no existe, queda vacío
        else:
            window['-OUTPUT-'].update("No hay destinos que coincidan con todos los filtros.\nIntenta cambiar el presupuesto o la temporada.")
            window['-IMAGE-'].update(data=None)

window.close()