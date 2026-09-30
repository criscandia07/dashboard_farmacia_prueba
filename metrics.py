import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def calculate_metrics(df_schedule, funciones, bloques):
    """Calcula horas totales y de ventanilla por TENS a partir de la planilla."""
    if df_schedule.empty:
        return pd.DataFrame(), {}

    # Mapa de duraciones por bloque (en horas)
    duraciones = {}
    for b in bloques:
        # Simplificación: 1.5 hrs bloque estándar, 1.0 hr colación
        duraciones[f"B{b['num']}"] = 1.0 if b["colacion"] else 1.5

    v_funcs = set(f["nombre"] for f in funciones if f.get("ventanilla"))
    
    bloque_cols = [c for c in df_schedule.columns if c.startswith("B")]
    
    tens_metrics = []
    for tens_id, group in df_schedule.groupby("TENS"):
        total_hrs = 0.0
        ventanilla_hrs = 0.0
        
        for _, row in group.iterrows():
            for b_col in bloque_cols:
                func_assigned = row[b_col]
                dur = duraciones.get(b_col, 1.0)
                total_hrs += dur
                if func_assigned in v_funcs:
                    ventanilla_hrs += dur

        tens_metrics.append({
            "TENS": tens_id,
            "Turno": group["Turno"].iloc[0],
            "Horas_Totales": total_hrs,
            "Horas_Ventanilla": ventanilla_hrs,
        })

    df_m = pd.DataFrame(tens_metrics)
    
    summary_kpis = {
        "tens_programados": len(df_m),
        "hrs_totales": df_m["Horas_Totales"].sum(),
        "hrs_promedio": df_m["Horas_Totales"].mean(),
        "hrs_vent_prom": df_m["Horas_Ventanilla"].mean(),
        "hrs_vent_max": df_m["Horas_Ventanilla"].max(),
        "diff_vent_max_min": df_m["Horas_Ventanilla"].max() - df_m["Horas_Ventanilla"].min()
    }
    
    return df_m, summary_kpis

def plot_horas_totales(df_m):
    """Gráfico de barras de Horas Totales con línea de promedio."""
    avg = df_m["Horas_Totales"].mean()
    fig = px.bar(
        df_m, x="TENS", y="Horas_Totales", color="Turno",
        title="Horas Totales Trabajadas por TENS",
        color_continuous_scale="Blues"
    )
    fig.add_hline(y=avg, line_dash="dash", line_color="#1E3A8A", annotation_text=f"Promedio ({avg:.1f}h)")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig

def plot_horas_ventanilla(df_m):
    """Gráfico de barras de Exposición a Ventanilla."""
    avg = df_m["Horas_Ventanilla"].mean()
    fig = px.bar(
        df_m, x="TENS", y="Horas_Ventanilla",
        title="Horas Acumuladas en Ventanilla (Recepción + Entrega)",
        color_discrete_sequence=["#3B82F6"]
    )
    fig.add_hline(y=avg, line_dash="dash", line_color="#EF4444", annotation_text=f"Promedio ({avg:.1f}h)")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig