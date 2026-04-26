import math

# Diámetros comerciales disponibles en metros y su peso en kg/m
DIAMETROS = {
    6:  {"d_m": 0.006,  "peso_kg_m": 0.222},
    8:  {"d_m": 0.008,  "peso_kg_m": 0.395},
    10: {"d_m": 0.010,  "peso_kg_m": 0.617},
    12: {"d_m": 0.012,  "peso_kg_m": 0.888},
    16: {"d_m": 0.016,  "peso_kg_m": 1.578},
    20: {"d_m": 0.020,  "peso_kg_m": 2.466},
    25: {"d_m": 0.025,  "peso_kg_m": 3.854},
}

def calcular_armadura_flexion(fc, fy, b, d, Mn, beta1, db_estribo=0.01):
    """
    Método de cálculo de armadura a flexión - CIRSOC 201-2005
    Retorna dict con todos los resultados intermedios y opciones de armadura.
    """
    resultados = {}

    # Momento nominal reducido
    Mnred = Mn / (fc * b * d**2)
    resultados["Mnred"] = round(Mnred, 6)

    # Índice de refuerzo efectivo
    We = (-1 + math.sqrt(1 - 2.352 * Mnred)) / (-1.176)
    resultados["We"] = round(We, 6)

    # Profundidad bloque de compresión equivalente
    a = We * d / 0.85
    resultados["a_m"] = round(a, 4)

    # Profundidad eje neutro
    c = a / beta1
    resultados["c_m"] = round(c, 4)

    # Curvatura
    fi = 0.003 / c
    resultados["fi"] = round(fi, 6)

    # Deformación en la armadura
    Ete = fi * (d - c)
    resultados["Ete"] = round(Ete, 6)

    # Verificación dominio tracción
    if Ete < 0.005:
        resultados["error"] = "Sección no controlada por tracción (εte < 0.005). Redimensionar viga."
        return resultados

    # Área de acero calculada
    As_calc = We * b * d * fc / fy
    resultados["As_calc_cm2"] = round(As_calc * 10000, 2)

    # Área de acero mínima (CIRSOC 201 §9.6.1)
    As_min1 = 0.25 * math.sqrt(fc) * b * d / fy
    As_min2 = 1.4 * b * d / fy
    As_min = max(As_min1, As_min2)
    resultados["As_min_cm2"] = round(As_min * 10000, 2)

    # Área de acero requerida
    As_req = max(As_calc, As_min)
    resultados["As_req_cm2"] = round(As_req * 10000, 2)

    # Selección de barras viables
    opciones = seleccionar_barras(As_req, b, d, db_estribo, fc, fy, beta1)
    resultados["opciones"] = opciones

    return resultados


def seleccionar_barras(As_req, b, d, db_estribo, fc, fy, beta1, sep_min=0.025):
    """
    Para cada diámetro comercial, calcula la cantidad mínima de barras
    que cubren As_req con separación >= sep_min (2.5 cm).
    Retorna lista de opciones viables con Md calculado.
    """
    r = 0.02  # recubrimiento fijo 2 cm
    opciones = []

    for ds_mm, datos in DIAMETROS.items():
        ds = datos["d_m"]
        As_barra = math.pi * ds**2 / 4

        # Cantidad mínima de barras para cubrir As_req
        n = math.ceil(As_req / As_barra)
        if n < 2:
            n = 2  # mínimo 2 barras

        # Verificar separación
        sep = (b - 2*r - 2*db_estribo - n*ds) / (n - 1)

        if sep < sep_min:
            continue  # separación insuficiente, diámetro no viable

        # Área real adoptada
        As_real = n * As_barra

        # Recalcular a y Md con As_real (todo en MN y m)
        a_real = As_real * fy / (0.85 * fc * b)
        Md_MNm = 0.9 * As_real * fy * (d - a_real / 2)
        Md_kNm = Md_MNm * 1000

        # Peso por metro lineal
        peso = n * datos["peso_kg_m"]

        opciones.append({
            "ds_mm": ds_mm,
            "n_barras": n,
            "As_real_cm2": round(As_real * 10000, 2),
            "separacion_cm": round(sep * 100, 1),
            "Md_kNm": round(Md_kNm, 2),
            "peso_kg_m": round(peso, 3),
        })

    return opciones