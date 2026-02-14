% locacion(Nombre, Provincia, Region)
locacion(bariloche, rio_negro, patagonia).
locacion(el_calafate, santa_cruz, patagonia).
locacion(ushuaia, tierra_del_fuego, patagonia).
locacion(mar_del_plata, buenos_aires, costa).
locacion(mendoza, mendoza, cuyo).
locacion(iguazu, misiones, litorial).
locacion(salta_capital, salta, norte).

% temporada_ideal(Locacion, Temporada)
temporada_ideal(bariloche, invierno).
temporada_ideal(bariloche, verano).
temporada_ideal(el_calafate, verano).
temporada_ideal(ushuaia, invierno).
temporada_ideal(mar_del_plata, verano).
temporada_ideal(mendoza, otono).
temporada_ideal(mendoza, primavera).
temporada_ideal(iguazu, invierno). % Mejor clima, menos calor sofocante

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

% actividad(Locacion, Actividad, Temporada)
actividad(bariloche, esqui, invierno).
actividad(bariloche, trekking, verano).
actividad(el_calafate, glaciar, verano).
actividad(ushuaia, navegar_canal_beagle, invierno).
actividad(mendoza, cata_vinos, otono).
actividad(mar_del_plata, playa, verano).
actividad(iguazu, cataratas, invierno).

% presupuesto_compatible(NivelElegido, NivelDestino)
presupuesto_compatible(bajo, bajo).
presupuesto_compatible(medio, bajo).
presupuesto_compatible(medio, medio).
presupuesto_compatible(alto, medio).
presupuesto_compatible(alto, alto).

% Recomendación general basada en 4 pilares
recomendar_destino(Destino, Temp, Pres, Comp, Act) :-
    temporada_ideal(Destino, Temp),
    presupuesto(Destino, Pres),
    adecuada_para(Destino, Comp),
    actividad(Destino, Act, Temp).

recomendar_destino(Destino, Temp, PresElegido, Comp, Act) :-
    temporada_ideal(Destino, Temp),
    presupuesto(Destino, PresDestino),           % Buscamos el presupuesto real del destino
    presupuesto_compatible(PresElegido, PresDestino), % Verificamos si entra en el rango
    adecuada_para(Destino, Comp),
    actividad(Destino, Act, Temp).

% ... (tus hechos de locacion, temporada_ideal, etc.).

% --- REGLAS PARA LA INTERFAZ (Copia esto tal cual) ---
lista_temporadas(L) :- setof(T, Loc^temporada_ideal(Loc, T), L).
lista_presupuestos(L) :- setof(P, Loc^presupuesto(Loc, P), L).
lista_companias(L) :- setof(C, Loc^adecuada_para(Loc, C), L).