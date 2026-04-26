# ──────────────────────────────────────────────────────────────────────────
# Cálculo de viga de hormigón armado — CIRSOC 201-2005
# Desarrollado por Ezequiel Raggio — Ingeniero Civil — Rosario, Argentina
# ──────────────────────────────────────────────────────────────────────────

import streamlit as st
from calculos.cargas import calcular_cargas
from calculos.flexion import calcular_armadura_flexion
from calculos.corte import calcular_armadura_corte

st.set_page_config(page_title="Viga HA", layout="wide")
st.title("Cálculo de viga de hormigón armado")
st.caption("CÁLCULOS BASADOS EN EL CIRSOC 201-2005")

# ─────────────────────────────────────────────
# SIDEBAR — Datos de entrada
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("Datos de entrada")

    st.subheader("Materiales")
    fc = st.number_input("f'c (MPa)", min_value=17.0, max_value=50.0, value=30.0, step=1.0)
    fy = st.number_input("fy (MPa)", min_value=420.0, max_value=420.0, value=420.0, step=1.0)

    st.subheader("Dimensiones")
    L = st.number_input("L (m)",    min_value=1.0,  max_value=20.0, value=7.0,  step=0.5)
    b = st.number_input("b (m)",    min_value=0.10, max_value=1.0,  value=0.30, step=0.05)
    h = st.number_input("h (m)",    min_value=0.10, max_value=2.0,  value=0.60, step=0.05)
    r = st.number_input("r (cm)",   min_value=1.0,  max_value=5.0,  value=2.0,  step=0.5)

    st.subheader("Cargas")
    Qd = st.number_input("Qd (kN/m)", min_value=0.0, value=12.0, step=1.0)
    Qs = st.number_input("Qs (kN/m)", min_value=0.0, value=8.0,  step=1.0)

    calcular = st.button("Calcular", use_container_width=True)

# ─────────────────────────────────────────────
# CÁLCULO — Se ejecuta al presionar Calcular
# ─────────────────────────────────────────────
if calcular:
    if h > 0.5 * L:
        st.error("La viga no es esbelta (h > 0.5·L). Redimensionar.")
        st.stop()

    r_m   = r / 100
    d     = h - r_m - 0.01
    beta1 = 0.85

    cargas = calcular_cargas(Qd, Qs, L)
    flex   = calcular_armadura_flexion(fc, fy, b, d, cargas["Mn"], beta1)
    corte  = calcular_armadura_corte(fc, fy, b, d, cargas["qu"], L)

    st.session_state["cargas"] = cargas
    st.session_state["flex"]   = flex
    st.session_state["corte"]  = corte
    st.session_state["d"]      = d
    st.session_state["Qd"]     = Qd
    st.session_state["Qs"]     = Qs
    st.session_state["L"]      = L
    st.session_state["fc"]     = fc
    st.session_state["fy"]     = fy
    st.session_state["b"]      = b
    st.session_state["h"]      = h
    st.session_state["beta1"]  = beta1

# ─────────────────────────────────────────────
# PANEL PRINCIPAL — Visible si hay resultados
# ─────────────────────────────────────────────
if "cargas" in st.session_state:
    cargas = st.session_state["cargas"]
    flex   = st.session_state["flex"]
    corte  = st.session_state["corte"]
    d      = st.session_state["d"]
    Qd     = st.session_state["Qd"]
    Qs     = st.session_state["Qs"]
    L      = st.session_state["L"]
    fc     = st.session_state["fc"]
    fy     = st.session_state["fy"]
    b      = st.session_state["b"]
    h      = st.session_state["h"]
    beta1  = st.session_state["beta1"]

    # ── BLOQUE 1: Solicitaciones ──────────────────────────────────────────
    st.subheader("Solicitaciones")

    # ELU1 y ELU2 con desarrollo visible, uno debajo del otro
    st.markdown(f"**ELU 1** = 1.4 · Qd = 1.4 × {Qd} = **{cargas['ELU1']} kN/m**")
    st.markdown(f"**ELU 2** = 1.2 · Qd + 1.6 · Qs = 1.2 × {Qd} + 1.6 × {Qs} = **{cargas['ELU2']} kN/m**")
    st.markdown(f"**qu** = max(ELU1, ELU2) = **{cargas['qu']} kN/m**")

    st.divider()

    # qu, Mu, Vu en fila con unidades al lado del valor
    col1, col2, col3 = st.columns(3)
    col1.metric(
        label="qu",
        value=f"{cargas['qu']} kN/m",
        help="Carga última de diseño: máximo entre ELU1 y ELU2"
    )
    col2.metric(
        label="Mu",
        value=f"{round(cargas['Mu'] * 1000, 1)} kN·m",
        help="Momento último: Mu = qu · L² / 8"
    )
    col3.metric(
        label="Vu(x=d)",
        value=f"{corte['Vu_d_kN']} kN",
        help="Cortante último a distancia d del apoyo: Vu(x=d) = qu · (L/2 - d)"
    )

    # ── BLOQUE 2: Flexión ─────────────────────────────────────────────────
    st.subheader("Flexión")

    if "error" in flex:
        st.error(flex["error"])
        st.stop()

    Mn_kNm = round(cargas["Mu"] * 1000 / 0.9, 1)

    # Mn destacado solo
    st.metric(
        label="Mn",
        value=f"{Mn_kNm} kN·m",
        help="Momento nominal requerido: Mn = Mu / φ = Mu / 0.9"
    )

    # Resultados intermedios en fila
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric(
        label="mnred",
        value=round(flex["Mnred"], 2),
        help="Momento nominal reducido: mnred = Mn / (f'c · b · d²)"
    )
    col2.metric(
        label="we",
        value=round(flex["We"], 2),
        help="Índice de refuerzo efectivo: we = (-1 + √(1 - 2.352·mnred)) / (-1.176)"
    )
    col3.metric(
        label="a",
        value=f"{round(flex['a_m'] * 100, 2)} cm",
        help="Profundidad del bloque de compresión equivalente: a = we · d / 0.85"
    )
    col4.metric(
        label="c",
        value=f"{round(flex['c_m'] * 100, 2)} cm",
        help="Profundidad del eje neutro: c = a / β1"
    )
    col5.metric(
        label="φ",
        value=f"{flex['fi']} 1/m",
        help="Curvatura de la sección: φ = εcu / c = 0.003 / c"
    )
    col6.metric(
        label="εte",
        value=f"{round(flex['Ete'] * 1000, 2)} ‰",
        help="Deformación de la armadura de tracción: εte = φ · (d - c) — debe ser ≥ 5‰"
    )

    # As req destacado solo
    st.metric(
        label="As req",
        value=f"{flex['As_req_cm2']} cm²",
        help="Área de acero requerida: As_req = max(As_calc, As_min)"
    )

    # Opciones de armadura a flexión
    st.markdown("**Opciones de armadura a flexión**")
    opciones_flex = flex["opciones"]
    if not opciones_flex:
        st.error("No hay opciones viables. Redimensionar sección.")
        st.stop()

    etiquetas_flex = [
        f"Φ{op['ds_mm']} × {op['n_barras']} barras | "
        f"As={op['As_real_cm2']} cm² | "
        f"sep={op['separacion_cm']} cm | "
        f"Md={op['Md_kNm']} kN·m | "
        f"peso={op['peso_kg_m']} kg/m"
        for op in opciones_flex
    ]

    eleccion_flex = st.radio("Seleccioná una opción:", etiquetas_flex, index=0)
    idx_flex = etiquetas_flex.index(eleccion_flex)
    op_flex  = opciones_flex[idx_flex]

    st.success(
        f"Adoptado: Φ{op_flex['ds_mm']} × {op_flex['n_barras']} barras — "
        f"As = {op_flex['As_real_cm2']} cm² — Md = {op_flex['Md_kNm']} kN·m"
    )

    with st.expander("Ver desarrollo completo — Flexión"):
        st.markdown(f"""
**Glosario de términos**
- **Mu**: Momento último — momento flector mayorado que actúa sobre la sección (kN·m)
- **φ**: Factor de reducción de resistencia a flexión = 0.90 (CIRSOC 201 §9.3)
- **Mn**: Momento nominal — resistencia nominal requerida: Mn = Mu / φ
- **mnred**: Momento nominal reducido — variable adimensional para el método de cálculo
- **we**: Índice de refuerzo efectivo — variable adimensional que relaciona la armadura con la sección
- **a**: Profundidad del bloque de compresión equivalente de Whitney (cm)
- **β1**: Factor del bloque rectangular equivalente = {beta1}
- **c**: Profundidad del eje neutro (cm)
- **εcu**: Deformación última del hormigón = 0.003 (CIRSOC 201 §10.2.3)
- **εte**: Deformación de la armadura de tracción (‰) — debe ser ≥ 5‰ (dominio tracción)
- **As calc**: Área de acero de cálculo — obtenida del método del índice de refuerzo (cm²)
- **As min**: Área de acero mínima reglamentaria (CIRSOC 201 §9.6.1) (cm²)
- **As req**: Área de acero requerida = max(As calc, As min) (cm²)
- **As**: Área de acero adoptada — según barras comerciales elegidas (cm²)
- **Md**: Momento de diseño — capacidad resistente de la sección con la armadura adoptada (kN·m)

**Desarrollo del cálculo**
```
Mu    = qu · L² / 8 = {cargas['qu']} · {L}² / 8 = {round(cargas['Mu']*1000,1)} kN·m
Mn    = Mu / φ = {round(cargas['Mu']*1000,1)} / 0.9 = {Mn_kNm} kN·m

mnred = Mn / (f'c · b · d²)
      = {Mn_kNm} / ({fc} · {b} · {round(d,3)}²)
      = {round(flex['Mnred'],4)}

we    = (-1 + √(1 - 2.352·mnred)) / (-1.176) = {round(flex['We'],4)}

a     = we · d / 0.85 = {round(flex['a_m']*100,2)} cm
c     = a / β1 = {round(flex['c_m']*100,2)} cm
φ     = 0.003 / c = {flex['fi']} 1/m
εte   = φ · (d - c) = {round(flex['Ete']*1000,2)} ‰  ≥ 5‰ → {'OK' if flex['Ete'] >= 0.005 else 'NO CUMPLE'}

As calc = we · b · d · f'c / fy = {flex['As_calc_cm2']} cm²
As min  = max(0.25·√f'c·b·d/fy , 1.4·b·d/fy) = {flex['As_min_cm2']} cm²
As req  = max(As calc, As min) = {flex['As_req_cm2']} cm²

Armadura adoptada: Φ{op_flex['ds_mm']} × {op_flex['n_barras']} barras
As      = {op_flex['As_real_cm2']} cm²
Md      = φ · As · fy · (d - a/2) = {op_flex['Md_kNm']} kN·m
```
        """)

    # ── BLOQUE 3: Corte ───────────────────────────────────────────────────
    st.subheader("Corte")

    if "error" in corte:
        st.error(corte["error"])
        st.stop()

    st.info(corte["aviso"])

    # Fila 1: Vn, Vc, Vs req
    col1, col2, col3 = st.columns(3)
    col1.metric(
        label="Vn = Vu/φ",
        value=f"{corte['Vn_kN']} kN",
        help="Cortante nominal requerido: Vn = Vu(x=d) / φv"
    )
    col2.metric(
        label="Vc",
        value=f"{corte['Vc_kN']} kN",
        help="Contribución del hormigón al corte: Vc = 0.17·√f'c·bw·d"
    )
    col3.metric(
        label="Vs req",
        value=f"{corte['Vs_req_kN']} kN",
        help="Cortante que debe tomar la armadura: Vs = Vn - Vc"
    )

    # Fila 2: Av calc/s, Av min/s, s max
    col1, col2, col3 = st.columns(3)
    col1.metric(
        label="Av calc/s",
        value=f"{corte['Avcalc_s_cm2m']} cm²/m",
        help="Armadura de corte de cálculo por metro lineal: Av calc/s = Vs / (fy · d)"
    )
    col2.metric(
        label="Av min/s",
        value=f"{corte['Avmin_s_cm2m']} cm²/m",
        help="Armadura mínima de corte por metro lineal (CIRSOC 201 §11.5.6.3)"
    )
    col3.metric(
        label="s max",
        value=f"{int(corte['s_max_m'] * 100)} cm",
        help="Separación máxima reglamentaria de estribos (CIRSOC 201 §11.5.5.1)"
    )

    st.markdown("**Opciones de armadura a corte**")
    opciones_corte = corte["opciones"]
    if not opciones_corte:
        st.error("No hay opciones viables. Redimensionar sección.")
        st.stop()

    etiquetas_corte = [
        f"Φ{op['db_mm']} c/{op['s_adopt_cm']}cm | "
        f"Av/s={op['Av_s_cm2m']} cm²/m | "
        f"Avmin/s={op['Avmin_s_cm2m']} cm²/m | "
        f"Vd={op['Vd_kN']} kN | "
        f"peso={op['peso_kg_m']} kg/m"
        for op in opciones_corte
    ]

    eleccion_corte = st.radio("Seleccioná una opción:", etiquetas_corte, index=0)
    idx_corte = etiquetas_corte.index(eleccion_corte)
    op_corte  = opciones_corte[idx_corte]

    st.success(
        f"Adoptado: Φ{op_corte['db_mm']} c/{op_corte['s_adopt_cm']}cm — "
        f"Vd = {op_corte['Vd_kN']} kN"
    )

    with st.expander("Ver desarrollo completo — Corte"):
        st.markdown(f"""
**Glosario de términos**
- **Vu(x=d)**: Cortante último a distancia d del apoyo — zona donde se diseña el corte (kN)
- **φv**: Factor de reducción de resistencia a corte = 0.75 (CIRSOC 201 §9.3)
- **Vn**: Cortante nominal requerido = Vu / φv (kN)
- **Vc**: Contribución del hormigón al corte: Vc = 0.17·√f'c·bw·d (kN)
- **Vs**: Cortante que debe tomar la armadura transversal: Vs = Vn - Vc (kN)
- **Av**: Área total de las ramas del estribo en una sección transversal (cm²)
- **Av/s**: Área de armadura de corte por metro lineal (cm²/m)
- **Avmin/s**: Área mínima de armadura de corte por metro lineal (CIRSOC 201 §11.5.6.3)
- **s**: Separación entre estribos adoptada (cm)
- **s max**: Separación máxima reglamentaria (CIRSOC 201 §11.5.5.1)
- **Vd**: Resistencia de diseño al corte con la armadura adoptada (kN)

**Desarrollo del cálculo**
```
Vu(x=d) = qu · (L/2 - d) = {cargas['qu']} · ({L}/2 - {round(d,3)}) = {corte['Vu_d_kN']} kN
Vn      = Vu / φv = {corte['Vu_d_kN']} / 0.75 = {corte['Vn_kN']} kN
Vc      = 0.17 · √{fc} · {b} · {round(d,3)} · 1000 = {corte['Vc_kN']} kN
Vs req  = Vn - Vc = {corte['Vn_kN']} - {corte['Vc_kN']} = {corte['Vs_req_kN']} kN

Avmin/s (cond. 1) = (1/16)·√f'c·b/fy = {corte['Avmin1_s_cm2m']} cm²/m
Avmin/s (cond. 2) = 0.33·b/fy        = {corte['Avmin2_s_cm2m']} cm²/m
Avmin/s governa   = {corte['Avmin_s_cm2m']} cm²/m

s max = min(d/2, 400mm) = {int(corte['s_max_m']*100)} cm

Estribo adoptado: Φ{op_corte['db_mm']} c/{op_corte['s_adopt_cm']}cm
Av/s    = {op_corte['Av_s_cm2m']} cm²/m
Vd      = {op_corte['Vd_kN']} kN
```
        """)

    # ── BLOQUE 4: Gráficos ────────────────────────────────────────────────
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    import numpy as np

    FS = 9  # tamaño de fuente uniforme para todos los gráficos

    st.subheader("Diagramas")

    qu   = cargas["qu"]
    Md   = op_flex["Md_kNm"]
    Vd   = op_corte["Vd_kN"]
    Ra   = qu * L / 2

    x    = np.linspace(0, L, 300)
    Mu_x = Ra * x - qu * x**2 / 2
    Vu_x = Ra - qu * x

    fig, (ax0, ax1, ax2) = plt.subplots(
        3, 1, figsize=(10, 9),
        facecolor='none',
        gridspec_kw={'height_ratios': [1, 2, 2]}
    )
    fig.patch.set_alpha(0)

    # — Gráfico 0: Vista lateral de la viga ——————————————————————————————
    ax0.set_xlim(0, L)
    ax0.set_ylim(-1, 2)
    ax0.set_facecolor('none')
    ax0.axis('off')

    viga = Rectangle((0, 0), L, 0.4, linewidth=1.5,
                     edgecolor='white', facecolor='#2a2a2a')
    ax0.add_patch(viga)

    ax0.fill([0,    -0.2,  0.2],  [-0.05, -0.45, -0.45], color='white')
    ax0.fill([L, L-0.2, L+0.2],  [-0.05, -0.45, -0.45], color='white')

    n_flechas  = 10
    xs_flechas = np.linspace(0.1, L-0.1, n_flechas)
    for xf in xs_flechas:
        ax0.annotate('', xy=(xf, 0.4), xytext=(xf, 1.2),
                     arrowprops=dict(arrowstyle='->', color='#378ADD', lw=1.2))
    ax0.plot([0.1, L-0.1], [1.2, 1.2], color='#378ADD', linewidth=1.5)
    ax0.text(L/2, 1.45, f'qu = {qu} kN/m', color='#378ADD',
             ha='center', va='bottom', fontsize=FS)

    ax0.annotate('', xy=(L, -0.6), xytext=(0, -0.6),
                 arrowprops=dict(arrowstyle='<->', color='gray', lw=1))
    ax0.text(L/2, -0.75, f'L = {L} m', color='gray',
             ha='center', va='top', fontsize=FS)

    # — Gráfico 1: Momento flector ————————————————————————————————————————
    ax1.plot(x, -Mu_x, color='#378ADD', linewidth=2, label='Mu(x)')
    ax1.axhline(y=-Md, color='#639922', linewidth=2, label=f'Md = {Md:.1f} kN·m')
    ax1.axhline(y=0, color='gray', linewidth=0.5)
    ax1.yaxis.grid(True, color='gray', linewidth=0.3, alpha=0.5)
    ax1.xaxis.grid(True, color='gray', linewidth=0.3, alpha=0.5)

    Mu_max = Mu_x.max()
    ax1.annotate(f'{Mu_max:.1f} kN·m',
                 xy=(L/2, -Mu_max), xytext=(L/2 + 0.8, -Mu_max * 0.75),
                 color='#378ADD', fontsize=FS,
                 arrowprops=dict(arrowstyle='->', color='#378ADD', lw=0.8))

    ax1.set_ylabel('Momento (kN·m)', color='white', fontsize=FS)
    ax1.tick_params(colors='white', labelsize=FS)
    ax1.set_facecolor('none')
    ax1.spines[:].set_color('gray')
    ax1.legend(facecolor='#1e1e1e', labelcolor='white', fontsize=FS)
    ax1.set_title('Diagrama de momento', color='white', fontsize=FS)
    ax1.set_xlim(0, L)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, _: f'{val:.1f}'))

    # — Gráfico 2: Corte ——————————————————————————————————————————————————
    ax2.plot(x, Vu_x, color='#378ADD', linewidth=2, label='Vu(x)')
    ax2.axhline(y=Vd,  color='#639922', linewidth=2, label=f'+Vd = {Vd:.1f} kN')
    ax2.axhline(y=-Vd, color='#639922', linewidth=2, label=f'-Vd = {-Vd:.1f} kN')
    ax2.axhline(y=0, color='gray', linewidth=0.5)
    ax2.yaxis.grid(True, color='gray', linewidth=0.3, alpha=0.5)
    ax2.xaxis.grid(True, color='gray', linewidth=0.3, alpha=0.5)

    ax2.axvline(x=d,   color='gray', linewidth=1, linestyle='--')
    ax2.axvline(x=L-d, color='gray', linewidth=1, linestyle='--')

    Vu_max = Vu_x.max()
    ax2.annotate(f'{Vu_max:.1f} kN',
                 xy=(0, Vu_max), xytext=(0.6, Vu_max * 0.65),
                 color='#378ADD', fontsize=FS,
                 arrowprops=dict(arrowstyle='->', color='#378ADD', lw=0.8))
    ax2.annotate(f'{-Vu_max:.1f} kN',
                 xy=(L, -Vu_max), xytext=(L - 1.2, -Vu_max * 0.65),
                 color='#378ADD', fontsize=FS,
                 arrowprops=dict(arrowstyle='->', color='#378ADD', lw=0.8))

    ticks_base  = list(ax2.get_xticks())
    ticks_extra = [round(d, 2), round(L-d, 2)]
    ticks_todos = sorted(set(ticks_base + ticks_extra))

    ax2.set_xticks(ticks_todos)
    ax2.set_xticklabels([
        f'd={round(d,2)}' if abs(t - d) < 0.01
        else f'L-d={round(L-d,2)}' if abs(t - (L-d)) < 0.01
        else f'{t:.1f}'
        for t in ticks_todos
    ], color='white', fontsize=FS)

    ax2.set_ylabel('Corte (kN)', color='white', fontsize=FS)
    ax2.set_xlabel('x (m)', color='white', fontsize=FS)
    ax2.tick_params(colors='white', labelsize=FS)
    ax2.set_facecolor('none')
    ax2.spines[:].set_color('gray')
    ax2.legend(facecolor='#1e1e1e', labelcolor='white', fontsize=FS)
    ax2.set_title('Diagrama de corte', color='white', fontsize=FS)
    ax2.set_xlim(0, L)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, _: f'{val:.1f}'))

    plt.tight_layout()
    st.pyplot(fig)
    plt.close()


# ── BLOQUE 5: Sección transversal con armadura ────────────────────────
    import matplotlib.patches as mpatches

    st.subheader("Sección transversal")

    ds    = op_flex["ds_mm"] / 1000   # diámetro barra longitudinal en m
    n     = op_flex["n_barras"]        # cantidad de barras
    db    = op_corte["db_mm"] / 1000  # diámetro estribo en m
    r_m   = r / 100                   # recubrimiento en m

    fig2, ax = plt.subplots(figsize=(2.5, 4), dpi=150, facecolor='none')
    fig2.patch.set_alpha(0)
    ax.set_facecolor('none')
    ax.set_aspect('equal')
    ax.axis('off')

    # Sección de hormigón
    seccion = mpatches.Rectangle(
        (0, 0), b, h,
        linewidth=1.5, edgecolor='white', facecolor='#2a2a2a'
    )
    ax.add_patch(seccion)

    # Estribo (rectángulo interior en rojo)
    margen_est = r_m + db / 2
    estribo = mpatches.Rectangle(
        (margen_est, margen_est),
        b - 2 * margen_est,
        h - 2 * margen_est,
        linewidth=max(1, db * 300),
        edgecolor='#E24B4A',
        facecolor='none'
    )
    ax.add_patch(estribo)

    # Barras longitudinales (fila inferior)
    y_barra  = r_m + db + ds / 2
    x_inicio = r_m + db + ds / 2
    x_fin    = b - r_m - db - ds / 2
    if n > 1:
        xs_barras = [x_inicio + i * (x_fin - x_inicio) / (n - 1) for i in range(n)]
    else:
        xs_barras = [(x_inicio + x_fin) / 2]

    radio_visual = ds / 2 * 1.5  # escala visual proporcional al diámetro
    for xb in xs_barras:
        barra = mpatches.Circle(
            (xb, y_barra), radius=radio_visual,
            color='#E24B4A'
        )
        ax.add_patch(barra)

    # Cotas y etiquetas — márgenes proporcionales a la sección
    margen_x = b * 0.15
    margen_y = h * 0.12

    ax.set_xlim(-margen_x, b + b * 0.55)
    ax.set_ylim(-margen_y, h + h * 0.08)

    # Cota b (ancho) — debajo de la sección
    y_cota_b = -margen_y * 0.6
    ax.annotate('', xy=(b, y_cota_b), xytext=(0, y_cota_b),
                arrowprops=dict(arrowstyle='<->', color='gray', lw=0.8))
    ax.text(b / 2, y_cota_b - margen_y * 0.3,
            f'b = {int(b*100)} cm',
            ha='center', va='top', color='gray', fontsize=7)

    # Cota h (altura) — a la derecha
    x_cota_h = b + b * 0.12
    ax.annotate('', xy=(x_cota_h, h), xytext=(x_cota_h, 0),
                arrowprops=dict(arrowstyle='<->', color='gray', lw=0.8))
    ax.text(x_cota_h + b * 0.04, h / 2,
            f'h = {int(h*100)} cm',
            ha='left', va='center', color='gray', fontsize=7)

    # Etiqueta armadura longitudinal
    ax.text(b / 2, y_barra - radio_visual - margen_y * 0.1,
            f'{n}Φ{op_flex["ds_mm"]}',
            ha='center', va='top', color='#E24B4A', fontsize=7)

    # Etiqueta estribo
    ax.text(b + b * 0.15, h * 0.75,
            f'Φ{op_corte["db_mm"]} c/{op_corte["s_adopt_cm"]}cm',
            ha='left', va='center', color='#E24B4A', fontsize=7)

    col_sec = st.columns([1, 2, 1])
    with col_sec[1]:
        st.pyplot(fig2)
    plt.close(fig2)

    # ── PIE DE PÁGINA ────────────────────────────────────────────────────────
    st.divider()
    st.caption('Desarrollado por Ezequiel Raggio — Ingeniero Civil — Rosario, Argentina')
