"""
Script de Generación de Gráficos — Capstone Analytics TDVRPTW
Genera las visualizaciones para la sección de Discusión de Resultados.

Ejecución:
    source capstone/bin/activate
    python pruebas_sensibilidad/generar_graficos.py

Salida: directorio documentacion/graficos/
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # backend sin GUI para generar archivos
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec
import seaborn as sns
from math import pi

warnings.filterwarnings("ignore")

# ─── Rutas ──────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "pruebas_sensibilidad", "resultados_combinaciones.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "documentacion", "graficos")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── Paleta y estilo global ──────────────────────────────────────────────────
PALETTE = {
    "bg":        "#0F1117",
    "surface":   "#1A1D27",
    "border":    "#2E3347",
    "accent1":   "#6C63FF",   # violeta principal
    "accent2":   "#3ECFCF",   # cian
    "accent3":   "#F7A440",   # naranja-dorado
    "accent4":   "#E05C7A",   # rosa-rojo
    "accent5":   "#5CE65C",   # verde
    "text":      "#E8EAED",
    "subtext":   "#9AA0B0",
}

ESCENARIOS = {
    "2026-12-04": "E1 – Alta Matutin",
    "2026-12-05": "E2 – Uniforme",
    "2026-12-06": "E3 – Alta Vespert.",
    "2026-12-07": "E4 – Mixto 50/50",
}

COLORS_ESC = [PALETTE["accent1"], PALETTE["accent2"],
              PALETTE["accent3"], PALETTE["accent4"]]

def apply_dark_style(fig, axes_list=None):
    fig.patch.set_facecolor(PALETTE["bg"])
    if axes_list is not None:
        for ax in axes_list:
            ax.set_facecolor(PALETTE["surface"])
            ax.tick_params(colors=PALETTE["subtext"], labelsize=9)
            ax.xaxis.label.set_color(PALETTE["text"])
            ax.yaxis.label.set_color(PALETTE["text"])
            ax.title.set_color(PALETTE["text"])
            for spine in ax.spines.values():
                spine.set_edgecolor(PALETTE["border"])

def save(fig, name):
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  ✓  {name}")
    return path

# ─── Carga de datos ──────────────────────────────────────────────────────────
def load_csv():
    df = pd.read_csv(CSV_PATH)
    df["Fecha"] = df["Fecha"].astype(str)
    return df

# ════════════════════════════════════════════════════════════════════════════
# GRÁFICO 1 — Composición de la Función Objetivo por Escenario (barras apiladas)
# ════════════════════════════════════════════════════════════════════════════
def grafico_1_composicion_fo():
    """Barras apiladas con los 3 componentes de la FO para la conf. óptima."""

    # KPIs extraídos de los archivos kpis_*.csv de la configuración de
    # referencia (pop=1500, n_gen=2500) — Sección 1.1 del documento
    data = {
        "Escenario": ["E1\nAlta Matutina\n(Día 04)", "E2\nUniforme\n(Día 05)",
                      "E3\nAlta Vespert.\n(Día 06)", "E4\nMixto 50/50\n(Día 07)"],
        "Transporte":    [830_999,   1_114_366,   920_899,  1_120_164],
        "Flota_Fija":    [2_000_000, 2_000_000, 2_000_000, 2_000_000],
        "Penalizacion":  [0,         3_380_412,   726_657,    475_301],
    }
    df_plot = pd.DataFrame(data)

    fig, ax = plt.subplots(figsize=(12, 6.5))
    apply_dark_style(fig, [ax])

    x = np.arange(len(df_plot))
    w = 0.55

    bar1 = ax.bar(x, df_plot["Flota_Fija"], width=w,
                  label="Costo Fijo de Flota", color=PALETTE["accent1"], alpha=0.92)
    bar2 = ax.bar(x, df_plot["Transporte"], width=w,
                  bottom=df_plot["Flota_Fija"],
                  label="Costo de Transporte", color=PALETTE["accent2"], alpha=0.92)
    bar3 = ax.bar(x, df_plot["Penalizacion"], width=w,
                  bottom=df_plot["Flota_Fija"] + df_plot["Transporte"],
                  label="Penalización por Espera", color=PALETTE["accent4"], alpha=0.92)

    # Etiquetas sobre cada barra con FO total
    totals = df_plot[["Transporte", "Flota_Fija", "Penalizacion"]].sum(axis=1)
    for i, (total, pct1, pct2) in enumerate(
        zip(totals,
            df_plot["Transporte"] / totals * 100,
            df_plot["Penalizacion"] / totals * 100)):
        ax.text(i, total + 120_000,
                f"${total/1e6:.2f}M",
                ha="center", va="bottom",
                color=PALETTE["text"], fontsize=10, fontweight="bold")

    # Línea de FO total
    ax.plot(x, totals, "o--", color=PALETTE["accent5"],
            linewidth=1.5, markersize=7, zorder=5, label="FO Total")

    ax.set_xticks(x)
    ax.set_xticklabels(df_plot["Escenario"], color=PALETTE["text"],
                       fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f"${v/1e6:.1f}M"))
    ax.set_ylabel("Función Objetivo ($)", fontsize=11)
    ax.set_title("Composición de la Función Objetivo por Escenario de Validación\n"
                 "Configuración óptima: pop=1.500, n_gen=2.500, holgura=30 min",
                 color=PALETTE["text"], fontsize=12, pad=14)
    ax.tick_params(axis="y", colors=PALETTE["subtext"])
    ax.set_ylim(0, totals.max() * 1.18)

    leg = ax.legend(loc="upper left", fontsize=9,
                    facecolor=PALETTE["surface"],
                    edgecolor=PALETTE["border"],
                    labelcolor=PALETTE["text"])

    ax.yaxis.grid(True, color=PALETTE["border"], linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)

    fig.tight_layout()
    return save(fig, "g1_composicion_fo_escenarios.png")


# ════════════════════════════════════════════════════════════════════════════
# GRÁFICO 2 — Heatmap pop_size × n_gen vs. Función Objetivo (Día 04 y 05)
# ════════════════════════════════════════════════════════════════════════════
def grafico_2_heatmap_sensibilidad():
    df = load_csv()

    fechas = {"2026-12-04": "Día 04 – Alta Demanda Matutina",
              "2026-12-05": "Día 05 – Distribución Uniforme"}

    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
    apply_dark_style(fig, axes)

    for ax, (fecha, titulo) in zip(axes, fechas.items()):
        sub = df[df["Fecha"] == fecha].copy()
        sub = sub.dropna(subset=["Funcion_Objetivo"])
        # Filtrar solo filas donde FO > 0 para no distorsionar con outliers de Day02
        sub = sub[sub["Funcion_Objetivo"] > 0]

        if sub.empty:
            ax.text(0.5, 0.5, "Sin datos", transform=ax.transAxes,
                    ha="center", va="center", color=PALETTE["text"])
            continue

        pivot = sub.pivot_table(values="Funcion_Objetivo",
                                index="pop_size", columns="n_gen",
                                aggfunc="min")
        pivot.sort_index(ascending=True, inplace=True)
        pivot = pivot.sort_index(axis=1)

        # Normalizar a millones para mejor legibilidad
        pivot_m = pivot / 1e6

        sns.heatmap(pivot_m,
                    ax=ax,
                    cmap="plasma_r",
                    annot=True,
                    fmt=".1f",
                    linewidths=0.4,
                    linecolor=PALETTE["bg"],
                    annot_kws={"size": 8, "color": PALETTE["text"]},
                    cbar_kws={"label": "F. Objetivo (M$)"},
                    )

        cbar = ax.collections[0].colorbar
        cbar.ax.yaxis.label.set_color(PALETTE["subtext"])
        cbar.ax.tick_params(colors=PALETTE["subtext"])

        ax.set_title(titulo, color=PALETTE["text"], fontsize=11, pad=10)
        ax.set_xlabel("n_gen (Generaciones)", fontsize=10)
        ax.set_ylabel("pop_size (Tamaño Población)", fontsize=10)
        ax.tick_params(colors=PALETTE["subtext"])

    fig.suptitle("Heatmap de Sensibilidad: Función Objetivo Mínima\n"
                 "según pop_size × n_gen (valores en millones de $)",
                 color=PALETTE["text"], fontsize=13, y=1.02)
    fig.tight_layout()
    return save(fig, "g2_heatmap_pop_gen.png")


# ════════════════════════════════════════════════════════════════════════════
# GRÁFICO 3 — Curva FO vs. pop_size por escenario (rodilla de mejora marginal)
# ════════════════════════════════════════════════════════════════════════════
def grafico_3_curva_fo_vs_popsize():
    df = load_csv()
    df = df[df["Funcion_Objetivo"] > 0]

    # Agrupar por fecha y pop_size — tomar el mínimo entre diferentes n_gen
    grp = (df.groupby(["Fecha", "pop_size"])["Funcion_Objetivo"]
             .min()
             .reset_index())

    fechas_plot = ["2026-12-04", "2026-12-05", "2026-12-06", "2026-12-07"]
    labels_map = {
        "2026-12-04": ("E1 – Alta Matutina (Día 04)", PALETTE["accent1"]),
        "2026-12-05": ("E2 – Uniforme (Día 05)",      PALETTE["accent2"]),
        "2026-12-06": ("E3 – Alta Vespert. (Día 06)", PALETTE["accent3"]),
        "2026-12-07": ("E4 – Mixto 50/50 (Día 07)",  PALETTE["accent4"]),
    }

    fig, ax = plt.subplots(figsize=(12, 6))
    apply_dark_style(fig, [ax])

    for fecha in fechas_plot:
        sub = grp[grp["Fecha"] == fecha].sort_values("pop_size")
        if sub.empty:
            continue
        label, color = labels_map[fecha]
        ax.plot(sub["pop_size"], sub["Funcion_Objetivo"] / 1e6,
                "o-", color=color, linewidth=2.2, markersize=7,
                label=label, zorder=4)
        # Anotar el valor del punto más bajo
        best = sub.loc[sub["Funcion_Objetivo"].idxmin()]
        ax.annotate(f"  ${best['Funcion_Objetivo']/1e6:.2f}M",
                    xy=(best["pop_size"], best["Funcion_Objetivo"]/1e6),
                    color=color, fontsize=8, va="center")

    # Zona de mejora marginal < 10%
    ax.axvspan(1200, 1600, alpha=0.07, color=PALETTE["accent5"],
               label="Zona de convergencia óptima (pop ≥ 1.500)")

    ax.set_xlabel("Tamaño de Población (pop_size)", fontsize=11)
    ax.set_ylabel("Función Objetivo Mínima (M$)", fontsize=11)
    ax.set_title("Curva de Mejora Marginal: Función Objetivo vs. Tamaño de Población\n"
                 "por Escenario de Validación (mejor n_gen para cada pop_size)",
                 color=PALETTE["text"], fontsize=12, pad=14)
    ax.yaxis.grid(True, color=PALETTE["border"], linestyle="--", alpha=0.5)
    ax.xaxis.grid(True, color=PALETTE["border"], linestyle=":", alpha=0.3)
    ax.set_axisbelow(True)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:.1f}M"))

    leg = ax.legend(fontsize=9, facecolor=PALETTE["surface"],
                    edgecolor=PALETTE["border"], labelcolor=PALETTE["text"])
    fig.tight_layout()
    return save(fig, "g3_fo_vs_popsize.png")


# ════════════════════════════════════════════════════════════════════════════
# GRÁFICO 4 — Scatter: Tiempo de Cómputo vs. Función Objetivo (Pareto empírico)
# ════════════════════════════════════════════════════════════════════════════
def grafico_4_scatter_tiempo_calidad():
    df = load_csv()
    df = df[df["Funcion_Objetivo"] > 0].copy()
    df["FO_M"] = df["Funcion_Objetivo"] / 1e6
    df["Escenario"] = df["Fecha"].map(ESCENARIOS).fillna(df["Fecha"])

    fig, ax = plt.subplots(figsize=(12, 7))
    apply_dark_style(fig, [ax])

    color_map = dict(zip(ESCENARIOS.values(), COLORS_ESC))

    for esc, sub in df.groupby("Escenario"):
        color = color_map.get(esc, "white")
        ax.scatter(sub["Tiempo_Computo_Min"], sub["FO_M"],
                   c=color, s=70, alpha=0.75, edgecolors=PALETTE["border"],
                   linewidths=0.5, label=esc, zorder=3)

    # Anotar la configuración óptima (menor FO, tiempo razonable < 30 min)
    optimas = df[(df["Funcion_Objetivo"] < 8e6) & (df["Tiempo_Computo_Min"] < 30)]
    if not optimas.empty:
        best = optimas.loc[optimas["Funcion_Objetivo"].idxmin()]
        ax.annotate(
            f"  Configuración óptima\n  pop={int(best['pop_size'])}, "
            f"gen={int(best['n_gen'])}\n  FO=${best['FO_M']:.2f}M | "
            f"t={best['Tiempo_Computo_Min']:.1f} min",
            xy=(best["Tiempo_Computo_Min"], best["FO_M"]),
            xytext=(best["Tiempo_Computo_Min"] + 5, best["FO_M"] + 1.5),
            color=PALETTE["accent5"],
            fontsize=8,
            arrowprops=dict(arrowstyle="->", color=PALETTE["accent5"],
                            lw=1.2)
        )
        ax.scatter([best["Tiempo_Computo_Min"]], [best["FO_M"]],
                   s=150, c=PALETTE["accent5"], zorder=6,
                   edgecolors="white", linewidths=1)

    ax.set_xlabel("Tiempo de Cómputo (min)", fontsize=11)
    ax.set_ylabel("Función Objetivo (M$)", fontsize=11)
    ax.set_title("Frontera Empírica Eficiencia–Calidad\n"
                 "Tiempo de Cómputo vs. Función Objetivo por Configuración y Escenario",
                 color=PALETTE["text"], fontsize=12, pad=14)
    ax.yaxis.grid(True, color=PALETTE["border"], linestyle="--", alpha=0.5)
    ax.xaxis.grid(True, color=PALETTE["border"], linestyle=":", alpha=0.3)
    ax.set_axisbelow(True)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:.0f}M"))

    leg = ax.legend(fontsize=9, facecolor=PALETTE["surface"],
                    edgecolor=PALETTE["border"], labelcolor=PALETTE["text"],
                    title="Escenario", title_fontsize=9)
    leg.get_title().set_color(PALETTE["subtext"])
    fig.tight_layout()
    return save(fig, "g4_scatter_tiempo_calidad.png")


# ════════════════════════════════════════════════════════════════════════════
# GRÁFICO 5 — Radar: KPIs normalizados por escenario
# ════════════════════════════════════════════════════════════════════════════
def grafico_5_radar_kpis():
    """Gráfico de araña con los KPIs clave normalizados (0-1) por escenario."""

    # Datos de KPI de la configuración de referencia (Sección 1.1)
    kpi_data = {
        "E1 Alta Matutina": {
            "% Entrega\na Tiempo":    91.6,
            "Kilometros\npor Pedido": 100 - (8.26 / 10.36) * 100,  # invertido (menor=mejor)
            "Utiliz.\nCapacidad":     83.3,
            "Vel. Computo\n(inv.)":   100 - (16.82 / 25.23) * 100,
            "Cobertura\nClientes":    100.0,
            "Emis. CO2\n(inv.)":      100 - (364.5 / 491.3) * 100,
        },
        "E2 Uniforme": {
            "% Entrega\na Tiempo":    88.1,
            "Kilometros\npor Pedido": 100 - (10.05 / 10.36) * 100,
            "Utiliz.\nCapacidad":     100.0,  # 107.8 → cap completada
            "Vel. Computo\n(inv.)":   100 - (14.57 / 25.23) * 100,
            "Cobertura\nClientes":    100.0,
            "Emis. CO2\n(inv.)":      100 - (488.8 / 491.3) * 100,
        },
        "E3 Alta Vespert.": {
            "% Entrega\na Tiempo":    100.0,
            "Kilometros\npor Pedido": 100 - (8.52 / 10.36) * 100,
            "Utiliz.\nCapacidad":     100.0,
            "Vel. Computo\n(inv.)":   100 - (13.87 / 25.23) * 100,
            "Cobertura\nClientes":    100.0,
            "Emis. CO2\n(inv.)":      100 - (403.9 / 491.3) * 100,
        },
        "E4 Mixto 50/50": {
            "% Entrega\na Tiempo":    98.3,
            "Kilometros\npor Pedido": 0.0,   # el peor (mayor distancia)
            "Utiliz.\nCapacidad":     100.0,
            "Vel. Computo\n(inv.)":   0.0,   # el más lento
            "Cobertura\nClientes":    100.0,
            "Emis. CO2\n(inv.)":      0.0,   # el peor
        },
    }

    categories = list(list(kpi_data.values())[0].keys())
    N = len(categories)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(9, 9),
                           subplot_kw=dict(projection="polar"))
    fig.patch.set_facecolor(PALETTE["bg"])
    ax.set_facecolor(PALETTE["surface"])

    for (label, vals), color in zip(kpi_data.items(), COLORS_ESC):
        values = [vals[c] for c in categories]
        values += values[:1]
        ax.plot(angles, values, linewidth=2, color=color, label=label, zorder=3)
        ax.fill(angles, values, color=color, alpha=0.12)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, color=PALETTE["text"], fontsize=9, va="center")
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"],
                       color=PALETTE["subtext"], fontsize=7)
    ax.yaxis.grid(True, color=PALETTE["border"], linestyle="--", alpha=0.5)
    ax.xaxis.grid(True, color=PALETTE["border"], linestyle=":", alpha=0.4)
    ax.spines["polar"].set_edgecolor(PALETTE["border"])

    ax.set_title("Perfil de Desempeño por Escenario\n(KPIs normalizados 0–100, mayor = mejor)",
                 color=PALETTE["text"], fontsize=12, pad=28)

    leg = ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15),
                    fontsize=9, facecolor=PALETTE["surface"],
                    edgecolor=PALETTE["border"], labelcolor=PALETTE["text"])

    fig.tight_layout()
    return save(fig, "g5_radar_kpis_escenarios.png")


# ════════════════════════════════════════════════════════════════════════════
# GRÁFICO 6 — Tiempo de cómputo vs. configuración GA (burbuja)
# ════════════════════════════════════════════════════════════════════════════
def grafico_6_tiempo_computo():
    """Comparativa de tiempos de cómputo por instancia y configuración clave."""

    data = {
        "Config":   ["pop=50\nn=1000", "pop=50\nn=1000", "pop=50\nn=1000", "pop=50\nn=1000",
                     "pop=200\nn=500",  "pop=200\nn=500",
                     "pop=200\nn=1000", "pop=200\nn=1000",
                     "pop=300\nn=1000", "pop=300\nn=1000",
                     "pop=1500\nn=2500","pop=1500\nn=2500","pop=1500\nn=2500","pop=1500\nn=2500"],
        "Día":      ["E1","E2","E3","E4",
                     "E1","E2",
                     "E1","E2",
                     "E1","E2",
                     "E1","E2","E3","E4"],
        "Tiempo":   [130.99, 7.42, 7.51, 8.48,
                     12.41, 12.37,
                     21.58, 21.39,
                     31.72, 31.65,
                     16.82, 14.57, 13.87, 25.23],
        "Clientes": [107, 63, 87, 95,
                     107, 118,
                     107, 118,
                     107, 118,
                     107, 118, 115, 115],
    }
    df_t = pd.DataFrame(data)

    fig, ax = plt.subplots(figsize=(13, 6.5))
    apply_dark_style(fig, [ax])

    color_map = {"E1": PALETTE["accent1"], "E2": PALETTE["accent2"],
                 "E3": PALETTE["accent3"], "E4": PALETTE["accent4"]}

    configs_uniq = df_t["Config"].unique()
    x_pos = {c: i for i, c in enumerate(configs_uniq)}
    jitter = {"E1": -0.15, "E2": -0.05, "E3": 0.05, "E4": 0.15}

    for _, row in df_t.iterrows():
        xj = x_pos[row["Config"]] + jitter.get(row["Día"], 0)
        color = color_map[row["Día"]]
        ax.scatter(xj, row["Tiempo"],
                   s=row["Clientes"] * 3.5,
                   c=color, alpha=0.82,
                   edgecolors=PALETTE["border"], linewidths=0.7, zorder=3)
        # Anotar outlier
        if row["Tiempo"] > 50:
            ax.annotate(f"  {row['Tiempo']:.0f} min\n  (outlier)",
                        xy=(xj, row["Tiempo"]),
                        color=PALETTE["accent4"], fontsize=7.5,
                        arrowprops=dict(arrowstyle="->",
                                        color=PALETTE["accent4"], lw=1))

    ax.set_xticks(list(x_pos.values()))
    ax.set_xticklabels(list(x_pos.keys()), color=PALETTE["text"], fontsize=9)
    ax.set_ylabel("Tiempo de Cómputo (min)", fontsize=11)
    ax.set_title("Tiempo de Cómputo por Configuración GA e Instancia\n"
                 "(tamaño de burbuja ∝ cantidad de clientes)",
                 color=PALETTE["text"], fontsize=12, pad=14)
    ax.yaxis.grid(True, color=PALETTE["border"], linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)

    # Sombrear zona óptima (pop=1500)
    ax.axvspan(x_pos["pop=1500\nn=2500"] - 0.45,
               x_pos["pop=1500\nn=2500"] + 0.45,
               alpha=0.07, color=PALETTE["accent5"])
    ax.text(x_pos["pop=1500\nn=2500"], ax.get_ylim()[1] * 0.92,
            "Conf. Óptima", ha="center", color=PALETTE["accent5"],
            fontsize=8, fontstyle="italic")

    # Leyenda manual de escenarios
    handles = [mpatches.Patch(color=c, label=f"{e}")
               for e, c in color_map.items()]
    leg = ax.legend(handles=handles, title="Escenario",
                    fontsize=9, title_fontsize=9,
                    facecolor=PALETTE["surface"],
                    edgecolor=PALETTE["border"],
                    labelcolor=PALETTE["text"])
    leg.get_title().set_color(PALETTE["subtext"])
    fig.tight_layout()
    return save(fig, "g6_tiempo_computo_instancias.png")


# ════════════════════════════════════════════════════════════════════════════
# GRÁFICO 7 — % Entregas a Tiempo vs. pop_size (líneas por escenario)
# ════════════════════════════════════════════════════════════════════════════
def grafico_7_entregas_vs_popsize():
    df = load_csv()
    df = df[df["Funcion_Objetivo"] > 0].copy()

    fechas_plot = ["2026-12-04", "2026-12-05", "2026-12-06", "2026-12-07"]
    labels_map = {
        "2026-12-04": ("E1 – Alta Matutina (Día 04)", PALETTE["accent1"]),
        "2026-12-05": ("E2 – Uniforme (Día 05)",      PALETTE["accent2"]),
        "2026-12-06": ("E3 – Alta Vespert. (Día 06)", PALETTE["accent3"]),
        "2026-12-07": ("E4 – Mixto 50/50 (Día 07)",  PALETTE["accent4"]),
    }

    grp = (df.groupby(["Fecha", "pop_size"])["Entregas_A_Tiempo_Pct"]
             .max().reset_index())

    fig, ax = plt.subplots(figsize=(12, 6))
    apply_dark_style(fig, [ax])

    for fecha in fechas_plot:
        sub = grp[grp["Fecha"] == fecha].sort_values("pop_size")
        if sub.empty:
            continue
        label, color = labels_map[fecha]
        ax.plot(sub["pop_size"], sub["Entregas_A_Tiempo_Pct"],
                "o-", color=color, linewidth=2.2, markersize=7,
                label=label, zorder=4)

    ax.axhline(100, color=PALETTE["accent5"], linestyle="--",
               linewidth=1.2, alpha=0.6, label="100% (objetivo ideal)")
    ax.axhline(95, color=PALETTE["subtext"], linestyle=":",
               linewidth=1, alpha=0.5, label="Umbral operativo 95%")

    ax.set_xlabel("Tamaño de Población (pop_size)", fontsize=11)
    ax.set_ylabel("% Entregas a Tiempo", fontsize=11)
    ax.set_title("Porcentaje de Entregas a Tiempo vs. Tamaño de Población\n"
                 "por Escenario de Validación",
                 color=PALETTE["text"], fontsize=12, pad=14)
    ax.set_ylim(60, 105)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.yaxis.grid(True, color=PALETTE["border"], linestyle="--", alpha=0.5)
    ax.xaxis.grid(True, color=PALETTE["border"], linestyle=":", alpha=0.3)
    ax.set_axisbelow(True)

    leg = ax.legend(fontsize=9, facecolor=PALETTE["surface"],
                    edgecolor=PALETTE["border"], labelcolor=PALETTE["text"])
    fig.tight_layout()
    return save(fig, "g7_entregas_vs_popsize.png")


# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "═" * 60)
    print("   Generador de Gráficos — Capstone Analytics TDVRPTW")
    print("═" * 60)
    print(f"  CSV origen  : {CSV_PATH}")
    print(f"  Salida       : {OUTPUT_DIR}")
    print()

    generated = []

    print("[1/7] Composición de la Función Objetivo por Escenario ...")
    generated.append(grafico_1_composicion_fo())

    print("[2/7] Heatmap pop_size × n_gen ...")
    generated.append(grafico_2_heatmap_sensibilidad())

    print("[3/7] Curva FO vs. pop_size (rodilla de mejora) ...")
    generated.append(grafico_3_curva_fo_vs_popsize())

    print("[4/7] Scatter Tiempo de Cómputo vs. Calidad ...")
    generated.append(grafico_4_scatter_tiempo_calidad())

    print("[5/7] Radar de KPIs por Escenario ...")
    generated.append(grafico_5_radar_kpis())

    print("[6/7] Tiempo de Cómputo por Configuración e Instancia ...")
    generated.append(grafico_6_tiempo_computo())

    print("[7/7] % Entregas a Tiempo vs. pop_size ...")
    generated.append(grafico_7_entregas_vs_popsize())

    print()
    print(f"  ✓  {len(generated)} gráficos generados en:")
    print(f"     {OUTPUT_DIR}")
    print("═" * 60 + "\n")
