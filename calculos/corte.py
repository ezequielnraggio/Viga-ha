import math

DIAMETROS_ESTRIBO = {
    6:  {"d_m": 0.006, "peso_kg_m": 0.222},
    8:  {"d_m": 0.008, "peso_kg_m": 0.395},
    10: {"d_m": 0.010, "peso_kg_m": 0.617},
}

def calcular_armadura_corte(fc, fy, b, d, qu, L):
    """
    Cálculo de armadura a corte - CIRSOC 201-2005
    qu: carga última (kN/m)
    L: luz de la viga (m)
    d: profundidad de la armadura (m)
    """
    resultados = {}

    # Cortante último a distancia d del apoyo
    Vu_d = qu * (L / 2 - d)
    resultados["Vu_d_kN"] = round(Vu_d, 2)

    # Cortante nominal
    phi_v = 0.75
    Vn = Vu_d / phi_v
    resultados["Vn_kN"] = round(Vn, 2)

    # Contribución del hormigón (kN)
    Vc = 0.17 * math.sqrt(fc) * b * d * 1000
    resultados["Vc_kN"]    = round(Vc, 2)
    resultados["phiVc_kN"] = round(phi_v * Vc, 2)

    # Vs requerido
    Vs_req = Vn - Vc
    resultados["Vs_req_kN"] = round(Vs_req, 2)

    # Verificación biela a compresión
    Vs_max_biela = (2/3) * math.sqrt(fc) * b * d * 1000
    resultados["Vs_max_biela_kN"] = round(Vs_max_biela, 2)

    if Vs_req > Vs_max_biela:
        resultados["error"] = "Biela a compresión no verifica (Vs > 2/3·√f'c·bw·d). Aumentar sección."
        return resultados

    # Aviso armadura mínima
    if Vu_d <= 0.5 * phi_v * Vc:
        resultados["aviso"] = "Vu ≤ 0.5·φ·Vc — no es requerida armadura mínima, pero se coloca igual."
    else:
        resultados["aviso"] = "Vu > 0.5·φ·Vc — se requiere armadura mínima."

    # s_max reglamentaria
    Vs_limite = (1/3) * math.sqrt(fc) * b * d * 1000
    if Vs_req > Vs_limite:
        s_max = min(d / 4, 0.200)
        resultados["s_max_aviso"] = "Vs > (1/3)·√f'c·bw·d → s_max reducida a la mitad"
    else:
        s_max = min(d / 2, 0.400)
    resultados["s_max_m"] = round(s_max, 3)

    # Av_min por metro lineal — dos ramas (CIRSOC 201 §11.5.6.3)
    Avmin_s1 = (1/16) * math.sqrt(fc) * b / fy
    Avmin_s2 = 0.33 * b / fy
    Avmin_s  = max(Avmin_s1, Avmin_s2)
    resultados["Avmin1_s_cm2m"] = round(Avmin_s1 * 10000, 2)
    resultados["Avmin2_s_cm2m"] = round(Avmin_s2 * 10000, 2)
    resultados["Avmin_s_cm2m"]  = round(Avmin_s  * 10000, 2)

    # Av_calc/s por metro lineal
    if Vs_req <= 0:
        Avcalc_s = 0
    else:
        Avcalc_s = (Vs_req / 1000) / (fy * d)
    resultados["Avcalc_s_cm2m"] = round(Avcalc_s * 10000, 2)

    # Av/s que gobierna
    Avgob_s = max(Avcalc_s, Avmin_s)
    resultados["Avgob_s_cm2m"] = round(Avgob_s * 10000, 2)

    # Selección de estribos
    opciones = seleccionar_estribos(Vs_req, fc, fy, b, d, s_max, Avmin_s, Avcalc_s)
    resultados["opciones"] = opciones

    return resultados


def seleccionar_estribos(Vs_req, fc, fy, b, d, s_max, Avmin_s, Avcalc_s, sep_min=0.050):
    """
    Para cada diámetro calcula s, trunca a entero en cm y recalcula Vd.
    """
    opciones = []

    Avmin_s_1rama  = Avmin_s / 2
    Avcalc_s_1rama = Avcalc_s / 2

    for db_mm, datos in DIAMETROS_ESTRIBO.items():
        db       = datos["d_m"]
        Av       = 2 * math.pi * db**2 / 4   # dos ramas (m²)
        Av_1rama = math.pi * db**2 / 4        # auxiliar: una rama (m²)

        # Av/s que gobierna (por rama)
        Avgob_s_1rama = max(Avmin_s_1rama, Avcalc_s_1rama)

        # Separación que cumple Av que gobierna
        s_req = Av_1rama / Avgob_s_1rama

        # Separación adoptada: mínimo entre s_req y s_max, truncada a entero
        s_final_cm = int(min(s_req, s_max) * 100)
        s_adopt    = s_final_cm / 100

        if s_adopt < sep_min:
            continue

        # Av/s y Avmin/s reales con s adoptada
        Av_s_real    = Av / s_adopt * 10000       # cm²/m
        Avmin_s_real = Avmin_s * s_adopt / s_adopt * 10000  # cm²/m (constante)

        # Vs y Vd reales
        Vs_real = Av * fy * d / s_adopt * 1000
        Vc      = 0.17 * math.sqrt(fc) * b * d * 1000
        Vd      = 0.75 * (Vc + Vs_real)

        # Peso por metro lineal (estribo cerrado)
        perimetro = 2 * (b + d)
        peso = (perimetro / s_adopt) * datos["peso_kg_m"]

        opciones.append({
            "db_mm":      db_mm,
            "s_adopt_cm": s_final_cm,
            "Av_s_cm2m":  round(Av_s_real, 2),
            "Avmin_s_cm2m": round(Avmin_s * 10000, 2),
            "Vd_kN":      round(Vd, 2),
            "peso_kg_m":  round(peso, 3),
        })

    return opciones