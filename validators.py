from datetime import datetime

def validate_configuration(params, tens_list, bloques, funciones, restricciones):
    """
    Realiza una validación rigurosa de todas las reglas de negocio e integridad.
    Retorna (is_valid: bool, errors: list, warnings: list).
    """
    errors = []
    warnings = []

    # 1. Validación de Personal TENS
    total_tens = len(tens_list)
    esperado_tens = params["cant_turnos"] * params["tens_por_turno"]
    if total_tens != esperado_tens:
        errors.append(
            f"Inconsistencia en personal: Existen {total_tens} TENS configurados, "
            f"pero se definieron {params['cant_turnos']} turnos de {params['tens_por_turno']} TENS cada uno (esperados: {esperado_tens})."
        )

    tens_ids = [t["id"] for t in tens_list]
    if len(tens_ids) != len(set(tens_ids)):
        errors.append("Existen identificadores (ID) de TENS duplicados en la lista de personal.")

    # 2. Validación de Bloques de Tiempo
    bloques_ordenados = sorted(bloques, key=lambda x: x["inicio"])
    for i in range(len(bloques_ordenados)):
        b = bloques_ordenados[i]
        try:
            t_in = datetime.strptime(b["inicio"], "%H:%M")
            t_fin = datetime.strptime(b["fin"], "%H:%M")
            if t_in >= t_fin:
                errors.append(f"Bloque {b['num']}: La hora de inicio ({b['inicio']}) debe ser menor que la de término ({b['fin']}).")
        except ValueError:
            errors.append(f"Bloque {b['num']}: Formato de hora inválido.")

        if i > 0:
            b_prev = bloques_ordenados[i-1]
            if b["inicio"] < b_prev["fin"]:
                errors.append(f"Superposición detectada entre el Bloque {b_prev['num']} (fin: {b_prev['fin']}) y Bloque {b['num']} (inicio: {b['inicio']}).")

    # Cobertura horaria institucional
    if bloques_ordenados:
        if bloques_ordenados[0]["inicio"] > "08:00":
            warnings.append("Los bloques no inician a las 08:00 hrs (Horario institucional CAE).")
        if bloques_ordenados[-1]["fin"] < "16:00":
            warnings.append("Los bloques finalizan antes de las 16:00 hrs.")

    # 3. Validación de Colaciones
    bloques_colacion = [b for b in bloques if b["colacion"]]
    if len(bloques_colacion) != 2:
        warnings.append(f"Se configuraron {len(bloques_colacion)} bloques de colación. El estándar del servicio es exactamente 2 bloques.")

    # 4. Validar Restricciones entre TENS
    for r in restricciones:
        if r["tens1"] not in tens_ids or r["tens2"] not in tens_ids:
            errors.append(f"Restricción inválida: Los TENS {r['tens1']} y/o {r['tens2']} no existen en el personal configurado.")

    # 5. Funciones
    colacion_func = [f for f in funciones if f.get("es_colacion")]
    if not colacion_func:
        errors.append("Debe existir al menos una función marcada como 'COLACIÓN'.")

    return len(errors) == 0, errors, warnings