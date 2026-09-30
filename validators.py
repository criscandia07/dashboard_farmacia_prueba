from datetime import datetime

def validate_configuration(params, tens_list, bloques, funciones, restricciones):
    errors = []
    warnings = []

    total_tens = len(tens_list)
    esperado_tens = params["cant_turnos"] * params["tens_por_turno"]
    if total_tens != esperado_tens:
        errors.append(
            f"Inconsistencia en personal: Existen {total_tens} TENS configurados, "
            f"pero se definieron {params['cant_turnos']} turnos de {params['tens_por_turno']} TENS (esperados: {esperado_tens})."
        )

    tens_ids = [t["id"] for t in tens_list]
    if len(tens_ids) != len(set(tens_ids)):
        errors.append("Existen identificadores (ID) de TENS duplicados en la lista de personal.")

    # Validar Bloques de Tiempo
    bloques_ordenados = sorted(bloques, key=lambda x: x["inicio"])
    for i in range(len(bloques_ordenados)):
        b = bloques_ordenados[i]
        try:
            t_in = datetime.strptime(b["inicio"], "%H:%M")
            t_fin = datetime.strptime(b["fin"], "%H:%M")
            if t_in >= t_fin:
                errors.append(f"Bloque {b['num']}: Hora inicio ({b['inicio']}) debe ser menor que fin ({b['fin']}).")
        except ValueError:
            errors.append(f"Bloque {b['num']}: Formato de hora inválido.")

        if i > 0:
            b_prev = bloques_ordenados[i-1]
            if b["inicio"] < b_prev["fin"]:
                errors.append(f"Superposición entre Bloque {b_prev['num']} y Bloque {b['num']}.")

    return len(errors) == 0, errors, warnings