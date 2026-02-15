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
perfil(mendoza, exploracion).|
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

% buscar_coincidencias(Destino, Temp, Pres, Comp, Perfil, Act)
buscar_coincidencias(Destino, Temp, PresUser, Comp, Perfil, Act) :-
    perfil(Destino, Perfil),
    temporada_ideal(Destino, Temp),
    presupuesto(Destino, PresDestino),
    presupuesto_compatible(PresUser, PresDestino),
    adecuada_para(Destino, Comp),
    actividad(Destino, Act, Temp).
% =================================================================
% 3. PREDICADOS PARA LA INTERFAZ [cite: 46]
% =================================================================

% Genera listas dinámicas para los menús desplegables de Python
lista_temporadas(L) :- setof(T, Loc^temporada_ideal(Loc, T), L).
lista_presupuestos(L) :- setof(P, Loc^presupuesto(Loc, P), L).
lista_companias(L) :- setof(C, Loc^adecuada_para(Loc, C), L).