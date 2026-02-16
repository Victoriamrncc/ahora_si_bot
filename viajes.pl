% =================================================================
% 1. BASE DE CONOCIMIENTOS (Hechos)
% =================================================================

% locacion(Nombre, Provincia) [cite: 51]
locacion(bariloche, rio_negro).
locacion(buenos_aires, buenos_aires).
locacion(el_calafate, santa_cruz).
locacion(ushuaia, tierra_del_fuego).
locacion(mar_del_plata, buenos_aires).
locacion(mendoza, mendoza).
locacion(iguazu, misiones).
locacion(salta_capital, salta).

% perfil(Destino, Estilo) [cite: 1402]
% Define la naturaleza del destino para el sistema experto
perfil(bariloche, aventura).
perfil(bariloche, exploracion).
perfil(buenos_aires, exploracion).
perfil(el_calafate, aventura).
perfil(ushuaia, descanso).
perfil(ushuaia, exploracion).
perfil(mar_del_plata, _).
perfil(mendoza, descanso).
perfil(mendoza, aventura).
perfil(iguazu, descanso).
perfil(iguazu, exploracion).
perfil(salta_capital, exploracion).

% temporada_ideal(Locacion, Temporada)
temporada_ideal(bariloche, invierno).
temporada_ideal(bariloche, verano).
temporada_ideal(mendoza, invierno).
temporada_ideal(mendoza, verano).
temporada_ideal(buenos_aires, invierno).
temporada_ideal(buenos_aires, verano).
temporada_ideal(el_calafate, verano).
temporada_ideal(ushuaia, invierno).
temporada_ideal(mar_del_plata, verano).
temporada_ideal(iguazu, invierno).
temporada_ideal(salta_capital, invierno).

% presupuesto(Locacion, Nivel)
presupuesto(bariloche, alto).
presupuesto(buenos_aires, medio).
presupuesto(el_calafate, alto).
presupuesto(ushuaia, alto).
presupuesto(mar_del_plata, bajo).
presupuesto(mendoza, medio).
presupuesto(salta_capital, bajo).
presupuesto(iguazu, bajo).

% adecuada_para(Locacion, Compania)
adecuada_para(bariloche, familia).
adecuada_para(el_calafate, pareja).
adecuada_para(buenos_aires, amigos).
adecuada_para(ushuaia, pareja).
adecuada_para(mar_del_plata, amigos).
adecuada_para(mendoza, pareja).
adecuada_para(salta_capital, familia).
adecuada_para(iguazu, familia).

% actividad(Locacion, Actividad, Temporada) [cite: 51]
actividad(bariloche, 'esqui', invierno).
actividad(bariloche, 'trekking', verano).
actividad(el_calafate, 'ver el glaciar', verano).
actividad(ushuaia, 'navegar canal beagle', invierno).
actividad(mendoza, 'cata de vinos', verano).
actividad(mar_del_plata, 'playa', verano).
actividad(iguazu, 'Las Cataratas del Iguazu', _).

% presupuesto_compatible(NivelUsuario, NivelDestino)
presupuesto_compatible(bajo, bajo).
presupuesto_compatible(medio, medio).
presupuesto_compatible(medio, bajo).
presupuesto_compatible(alto, alto).
presupuesto_compatible(alto, medio).

% Distancias (grafo pesado dirigido, luego lo hacemos bidireccional)
dist(bariloche, el_calafate, 1430).
dist(bariloche, mendoza, 1215).
dist(el_calafate, ushuaia, 880).
dist(mendoza, salta_capital, 1260).
dist(mendoza, buenos_aires, 1050).
dist(buenos_aires, iguazu, 1290).
dist(buenos_aires, mar_del_plata, 415).
dist(iguazu, salta_capital, 1120).


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
% Redefinimos para que use la lógica detallada
recomendar_destino(Destino, Temp, PresUser, Comp, Act, Explicacion) :-
    buscar_coincidencias_detallada(Destino, Temp, PresUser, Comp, _, Act, Explicacion).

% Justificación de la recomendación (Explicabilidad Amigable)
explicar(Destino, Temp, _PresUser, _Comp, Perfil, Act, Mensaje) :-
    locacion(Destino, Prov),
    atomic_list_concat([
        'Analice tu perfil y ', Destino, ' (', Prov, ') es la opcion ideal para vos porque encaja con tu estilo de ', Perfil,
        '. Si vas en ', Temp, ', vas a poder disfrutar de actividades como ', Act, '.'
    ], Mensaje).

% Motor de inferencia
buscar_coincidencias_detallada(Destino, Temp, PresUser, Comp, Perfil, Act, Explicacion) :-
    perfil(Destino, Perfil),
    temporada_ideal(Destino, Temp),
    presupuesto(Destino, PresDestino),
    presupuesto_compatible(PresUser, PresDestino),
    (adecuada_para(Destino, Comp) ; true),   % Si no coincide la compañía, no bloquea
    (actividad(Destino, Act, Temp) ; Act = 'explorar la ciudad'),
    explicar(Destino, Temp, PresUser, Comp, Perfil, Act, Explicacion).

% =================================================================
% 3. PREDICADOS PARA LA INTERFAZ [cite: 46]
% =================================================================

% Genera listas dinámicas para los menús desplegables de Python
lista_temporadas(L) :- setof(T, Loc^temporada_ideal(Loc, T), L).
lista_presupuestos(L) :- setof(P, Loc^presupuesto(Loc, P), L).
lista_companias(L) :- setof(C, Loc^adecuada_para(Loc, C), L).
lista_destinos(L) :-
    setof(X, Y^D^(dist(X,Y,D);dist(Y,X,D)), L).

% =================================================================
% 4. GRAFO Y LÓGICA TSP (Problema del Viajante)
% =================================================================

% 1. CONEXIÓN BÁSICA
conectado(A, B, D) :- dist(A, B, D).
conectado(A, B, D) :- dist(B, A, D).

% 2. DISTANCIA MÍNIMA CON ESCALAS
% Usamos aggregate_all para obtener solo el número de la distancia mas corta.
distancia_puntos(A, B, DMin) :-
    aggregate_all(min(D), camino_recursivo(A, B, [A], D), DMin).

camino_recursivo(A, B, _, D) :- conectado(A, B, D).
camino_recursivo(A, B, V, D) :- 
    conectado(A, C, D1), 
    \+ member(C, V), 
    camino_recursivo(C, B, [C|V], D2), 
    D is D1 + D2.

% 3. SUMAR TRAMOS DE LA PERMUTACIÓN
% Suma las distancias de los saltos entre ciudades de la lista.
calcular_tramos([_], 0).
calcular_tramos([C1, C2 | Resto], Total) :-
    distancia_puntos(C1, C2, D),
    calcular_tramos([C2 | Resto], Sub),
    Total is D + Sub.

% 4. MEJOR RUTA (SIN REGRESO AL INICIO)
mejor_ruta(Ciudades, MejorRuta, DistanciaMinima) :-
    setof([D, P], (
        permutation(Ciudades, P),
        calcular_tramos(P, D) % <--- Aquí ya no sumamos el regreso
    ), [[DistanciaMinima, MejorRuta] | _]).

%=================================================================
% --- MÁQUINA DE TURING: VALIDADOR DE FORMATO (LLLNNNN) ---
%=================================================================

% Predicados auxiliares (Ponelos arriba de todo) [cite: 1098]
es_letra(X) :- member(X, [a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z]).
es_numero(N) :- member(N, ['0','1','2','3','4','5','6','7','8','9']).

% Bloque de transiciones delta/5 (Todos juntos ahora) [cite: 861]
delta(q0, L, q1, L, r) :- es_letra(L).
delta(q1, L, q2, L, r) :- es_letra(L).
delta(q2, L, q3, L, r) :- es_letra(L).
delta(q3, N, q4, N, r) :- es_numero(N).
delta(q4, N, q5, N, r) :- es_numero(N).
delta(q5, N, q6, N, r) :- es_numero(N).
delta(q6, N, q7, N, r) :- es_numero(N).
delta(q7, b, q_accept, b, r). % Verificación de final de cadena (Blanco) [cite: 865, 866]

% Resto del motor de la MT y validación... [cite: 857, 1085]
validar_ticket(String, "Ticket VALIDO - Formato Correcto") :-
    string_lower(String, Lower),
    atom_chars(Lower, Lista),
    append(Lista, [b], Cinta), % El simbolo 'b' representa el Blanco 'B' de la teoría [cite: 843, 872]
    ejecutar_mt(q0, Cinta, 0), !.

validar_ticket(_, "Ticket INVALIDO - Error de Sintaxis").

ejecutar_mt(q_accept, _, _) :- !. % Aceptación por parada [cite: 1091, 1093]
ejecutar_mt(Estado, Cinta, Pos) :-
    nth0(Pos, Cinta, Simbolo),
    delta(Estado, Simbolo, NuevoEstado, _, r),
    NuevaPos is Pos + 1,
    ejecutar_mt(NuevoEstado, Cinta, NuevaPos).

% =================================================================
% 6. AUTOMATA FINITO (Ciclo de Vida del Asistente)
% =================================================================
% transicion(EstadoActual, Evento, SiguienteEstado)

transicion(inicio, abrir_app, esperando_perfil).
transicion(esperando_perfil, ingresar_datos, calculando_destino).
transicion(calculando_destino, mostrar_resultado, destino_mostrado).
transicion(destino_mostrado, pedir_ruta, calculando_tsp).
transicion(calculando_tsp, mostrar_ruta, ruta_lista).
transicion(ruta_lista, validar_ticket, validando_mt).
transicion(validando_mt, ticket_ok, finalizado).
transicion(finalizado, reiniciar, inicio).

% Predicado de consulta para la lógica del autómata
proximo_paso(Actual, Evento, Siguiente) :- transicion(Actual, Evento, Siguiente).