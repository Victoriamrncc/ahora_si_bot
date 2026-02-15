% =================================================================
% 1. BASE DE CONOCIMIENTOS (Hechos)
% =================================================================

% locacion(Nombre, Provincia, Region) [cite: 51]
locacion(bariloche, rio_negro, patagonia).
locacion(el_calafate, santa_cruz, patagonia).
locacion(ushuaia, tierra_del_fuego, patagonia).
locacion(mar_del_plata, buenos_aires, costa).
locacion(mendoza, mendoza, cuyo).
locacion(iguazu, misiones, litorial).
locacion(salta_capital, salta, norte).

% perfil(Destino, Estilo) [cite: 1402]
% Define la naturaleza del destino para el sistema experto
perfil(bariloche, aventura).
perfil(bariloche, exploracion).
perfil(el_calafate, aventura).
perfil(ushuaia, descanso).
perfil(mar_del_plata, descanso).
perfil(mendoza, exploracion).
perfil(iguazu, aventura).
perfil(salta_capital, exploracion).

% temporada_ideal(Locacion, Temporada)
temporada_ideal(bariloche, invierno).
temporada_ideal(bariloche, verano).
temporada_ideal(el_calafate, verano).
temporada_ideal(ushuaia, invierno).
temporada_ideal(mar_del_plata, verano).
temporada_ideal(mendoza, otono).
temporada_ideal(mendoza, primavera).
temporada_ideal(iguazu, invierno).

% presupuesto(Locacion, Nivel)
presupuesto(bariloche, alto).
presupuesto(el_calafate, alto).
presupuesto(ushuaia, alto).
presupuesto(mar_del_plata, bajo).
presupuesto(mendoza, medio).
presupuesto(salta_capital, bajo).

% adecuada_para(Locacion, Compania)
adecuada_para(bariloche, amigos).
adecuada_para(bariloche, familia).
adecuada_para(el_calafate, pareja).
adecuada_para(ushuaia, pareja).
adecuada_para(mar_del_plata, amigos).
adecuada_para(mendoza, pareja).
adecuada_para(salta_capital, familia).

% actividad(Locacion, Actividad, Temporada) [cite: 51]
actividad(bariloche, esqui, invierno).
actividad(bariloche, trekking, verano).
actividad(el_calafate, glaciar, verano).
actividad(ushuaia, navegar_canal_beagle, invierno).
actividad(mendoza, cata_vinos, otono).
actividad(mar_del_plata, playa, verano).
actividad(iguazu, cataratas, invierno).

% presupuesto_compatible(NivelUsuario, NivelDestino)
presupuesto_compatible(bajo, bajo).
presupuesto_compatible(medio, medio).
presupuesto_compatible(medio, bajo).
presupuesto_compatible(alto, alto).
presupuesto_compatible(alto, medio).


% =================================================================
% MÁQUINA DE INFERENCIA (Lógica de Perfiles)
% =================================================================

% Máquina de Inferencia: Perfiles Acumulativos
% Ahora, si el usuario marca "si" en dos opciones, Prolog devolverá AMBAS.
determinar_perfil(aventura, si, _, _).
determinar_perfil(exploracion, _, si, _).
determinar_perfil(descanso, _, _, si).
determinar_perfil(exploracion, no, no, no).

% recomendar_destino(Destino, Temp, Pres, Comp, Act) 
% Se define el objetivo para que Python lo consulte directamente.
recomendar_destino(Destino, Temp, Pres, Comp, Act) :-
    buscar_coincidencias(Destino, Temp, Pres, Comp, _, Act).

% Justificación de la recomendación (Explicabilidad Amigable)
explicar(Destino, Temp, _PresUser, _Comp, Perfil, Act, Mensaje) :-
    locacion(Destino, Prov, _Reg),
    atomic_list_concat([
        'Analicé tu perfil y ', Destino, ' (', Prov, ') es la opción ideal para vos porque encaja con tu estilo de ', Perfil, 
        '. Si vas en ', Temp, ', vas a poder disfrutar de actividades como ', Act, '.'
    ], Mensaje).

% Motor de inferencia
buscar_coincidencias_detallada(Destino, Temp, PresUser, Comp, Perfil, Act, Explicacion) :-
    perfil(Destino, Perfil),
    temporada_ideal(Destino, Temp),
    presupuesto(Destino, PresDestino),
    presupuesto_compatible(PresUser, PresDestino), % La lógica del dinero sigue funcionando internamente
    adecuada_para(Destino, Comp),
    actividad(Destino, Act, Temp),
    explicar(Destino, Temp, PresUser, Comp, Perfil, Act, Explicacion).
% =================================================================
% 3. PREDICADOS PARA LA INTERFAZ [cite: 46]
% =================================================================

% Genera listas dinámicas para los menús desplegables de Python
lista_temporadas(L) :- setof(T, Loc^temporada_ideal(Loc, T), L).
lista_presupuestos(L) :- setof(P, Loc^presupuesto(Loc, P), L).
lista_companias(L) :- setof(C, Loc^adecuada_para(Loc, C), L).

% =================================================================
% 4. GRAFO Y LÓGICA TSP (Problema del Viajante)
% =================================================================

% Distancias entre ciudades (Grafo pesado)
dist(bariloche, el_calafate, 1430).
dist(bariloche, mendoza, 1215).
dist(el_calafate, ushuaia, 880).
dist(mendoza, salta_capital, 1260).
dist(mendoza, buenos_aires, 1050).
dist(buenos_aires, iguazu, 1290).
dist(buenos_aires, mar_del_plata, 415).
dist(iguazu, salta_capital, 1120).

% Regla para que el camino sea bidireccional
conectado(A, B, D) :- dist(A, B, D).
conectado(A, B, D) :- dist(B, A, D).

% Predicado para obtener la lista de destinos para la interfaz
lista_destinos(L) :- setof(D, P^R^locacion(D, P, R), L).

% Algoritmo para calcular la distancia total de una lista
ruta_total([_], 0).
ruta_total([C1, C2 | Resto], Total) :-
    conectado(C1, C2, D),
    ruta_total([C2 | Resto], Sub),
    Total is D + Sub.

% Encuentra la mejor ruta entre un conjunto de ciudades
mejor_ruta(Ciudades, MejorRuta, DistanciaMinima) :-
    findall([Ruta, Dist], (permutation(Ciudades, Ruta), ruta_total(Ruta, Dist)), Combinaciones),
    sort(2, @=<, Combinaciones, [[MejorRuta, DistanciaMinima] | _]).