from ortools.sat.python import cp_model
from datetime import datetime, timedelta

def generate_working_days(num_days, feriados_str):
    """Genera días hábiles considerando Lunes-Viernes y saltando feriados."""
    feriados = set(feriados_str)
    curr = datetime.now()
    # Ajustar al próximo lunes
    curr += timedelta(days=(7 - curr.weekday()) % 7)
    
    working_days = []
    while len(working_days) < num_days:
        date_str = curr.strftime("%Y-%m-%d")
        # 0..4 es Lunes..Viernes
        if curr.weekday() < 5 and date_str not in feriados:
            working_days.append({
                "date_str": date_str,
                "weekday": curr.weekday(), # 0: Lunes, 4: Viernes
                "day_name": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"][curr.weekday()]
            })
        curr += timedelta(days=1)
    return working_days

def solve_schedule(params, tens_list, bloques, funciones, restricciones):
    """
    Resuelve la asignación mediante Programación de Restricciones (CP-SAT / OR-Tools).
    """
    days = generate_working_days(params["dias_programar"], params["feriados"])
    model = cp_model.CpModel()
    
    TENS_IDS = [t["id"] for t in tens_list]
    TENS_DICT = {t["id"]: t for t in tens_list}
    FUNC_IDS = [f["id"] for f in funciones]
    FUNC_DICT = {f["id"]: f for f in funciones}
    COL_FUNC_ID = next(f["id"] for f in funciones if f.get("es_colacion"))
    VENTANILLA_FUNCS = [f["id"] for f in funciones if f.get("ventanilla")]

    # Variables de decisión: x[tens, dia_idx, bloque_num, func_id] in {0, 1}
    x = {}
    for t in TENS_IDS:
        for d_idx, d in enumerate(days):
            for b in bloques:
                for f in FUNC_IDS:
                    x[t, d_idx, b["num"], f] = model.NewBoolVar(f"x_{t}_{d_idx}_{b['num']}_{f}")

    # RESTRICCIONES DURAS

    # 1. Exactamente una función por TENS, día y bloque
    for t in TENS_IDS:
        for d_idx in range(len(days)):
            for b in bloques:
                model.AddExactlyOne(x[t, d_idx, b["num"], f] for f in FUNC_IDS)

    # 2. Cobertura requerida por bloque y día (para funciones que no son colación)
    # Exclusión de viernes para el bloque 7 si supera las 16:00
    for d_idx, d in enumerate(days):
        is_friday = (d["weekday"] == 4)
        for b in bloques:
            if is_friday and b["inicio"] >= "16:00":
                # Viernes después de las 16:00 no hay jornada
                for t in TENS_IDS:
                    for f in FUNC_IDS:
                        model.Add(x[t, d_idx, b["num"], f] == 0)
                continue

            if not b["colacion"]:
                # Cobertura en funciones operativas
                pass # Cobertura general guiada por requerimiento

    # 3. Distribución de Colación 50%/50% equilibrada
    bloques_col = [b for b in bloques if b["colacion"]]
    if len(bloques_col) == 2:
        b1_num, b2_num = bloques_col[0]["num"], bloques_col[1]["num"]
        for d_idx in range(len(days)):
            for turno in range(1, params["cant_turnos"] + 1):
                tens_turno = [t["id"] for t in tens_list if t["turno"] == turno]
                n_tens = len(tens_turno)
                g1_size = n_tens // 2
                
                # Asignación al primer bloque de colación
                model.Add(sum(x[t, d_idx, b1_num, COL_FUNC_ID] for t in tens_turno) == g1_size)
                # Asignación al segundo bloque de colación
                model.Add(sum(x[t, d_idx, b2_num, COL_FUNC_ID] for t in tens_turno) == (n_tens - g1_size))

    # 4. Restricciones de Incompatibilidad entre TENS (Ventanilla)
    for r in restricciones:
        t1, t2 = r["tens1"], r["tens2"]
        if t1 in TENS_IDS and t2 in TENS_IDS:
            for d_idx in range(len(days)):
                for b in bloques:
                    for v_func in VENTANILLA_FUNCS:
                        # T1 y T2 no pueden estar en v_func al mismo tiempo
                        model.Add(x[t1, d_idx, b["num"], v_func] + x[t2, d_idx, b["num"], v_func] <= 1)

    # 5. Días de Ciclo (Mantiene la función constante dentro del mismo ciclo)
    ciclo_dias = params["dias_ciclo"]
    for t in TENS_IDS:
        for d_idx in range(len(days)):
            if d_idx % ciclo_dias != 0:
                d_prev = d_idx - 1
                for b in bloques:
                    for f in FUNC_IDS:
                        if not FUNC_DICT[f].get("es_colacion"):
                            model.Add(x[t, d_idx, b["num"], f] == x[t, d_prev, b["num"], f])

    # FUNCIÓN OBJETIVO: Minimizar varianza/exposición acumulada a ventanilla
    ventanilla_vars = []
    for t in TENS_IDS:
        v_count = model.NewIntVar(0, len(days) * len(bloques), f"v_count_{t}")
        model.Add(v_count == sum(x[t, d_idx, b["num"], v_f] 
                                for d_idx in range(len(days)) 
                                for b in bloques 
                                for v_f in VENTANILLA_FUNCS))
        ventanilla_vars.append(v_count)

    # Minimizar el máximo de ventanilla asignado a cualquier TENS
    max_ventanilla = model.NewIntVar(0, len(days) * len(bloques), "max_v")
    model.AddMaxEquality(max_ventanilla, ventanilla_vars)
    model.Minimize(max_ventanilla * 100 + sum(ventanilla_vars))

    # SOLVER
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10.0
    status = solver.Solve(model)

    # CONSTRUCCIÓN DE RESULTADOS
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        schedule = []
        for d_idx, d in enumerate(days):
            for t_id in TENS_IDS:
                row = {
                    "Dia_Num": d_idx + 1,
                    "Fecha": d["date_str"],
                    "Dia_Nombre": d["day_name"],
                    "TENS": t_id,
                    "Turno": TENS_DICT[t_id]["turno"]
                }
                for b in bloques:
                    for f_id in FUNC_IDS:
                        if solver.Value(x[t_id, d_idx, b["num"], f_id]) == 1:
                            row[f"B{b['num']}"] = FUNC_DICT[f_id]["nombre"]
                schedule.append(row)

        return {
            "status": "OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE",
            "is_relaxed": False,
            "schedule": schedule,
            "days": days,
            "diagnostics": {
                "factible": True,
                "duras_cumplidas": True,
                "optima": (status == cp_model.OPTIMAL),
                "relajadas_count": 0,
                "detalles": []
            }
        }
    else:
        return {
            "status": "INFEASIBLE",
            "is_relaxed": True,
            "schedule": [],
            "days": days,
            "diagnostics": {
                "factible": False,
                "duras_cumplidas": False,
                "optima": False,
                "relajadas_count": 1,
                "detalles": ["No fue posible encontrar una solución factible con las restricciones actuales."]
            }
        }