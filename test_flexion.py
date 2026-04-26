from calculos.cargas import calcular_cargas
from calculos.flexion import calcular_armadura_flexion

# Datos del Word
Qd   = 12      # kN/m
Qs   = 8       # kN/m
L    = 7       # m
fc   = 30      # MPa
fy   = 420     # MPa
b    = 0.30    # m
h    = 0.60    # m
d    = 0.56    # m  (h - r - db_estribo - 1cm)
beta1 = 0.85

# Cargas
cargas = calcular_cargas(Qd, Qs, L)
print("=== CARGAS ===")
unidades_cargas = {
    "ELU1": "kN/m",
    "ELU2": "kN/m",
    "qu":   "kN/m",
    "Mu":   "MN·m",
    "Mn":   "MN·m",
}
for k, v in cargas.items():
    u = unidades_cargas.get(k, "")
    print(f"  {k}: {v} {u}".strip())

# Flexión
Mn = cargas["Mn"]
print("\n=== FLEXIÓN ===")
unidades_flex = {
    "Mnred":       "",
    "We":          "",
    "a_m":         "m",
    "c_m":         "m",
    "fi":          "1/m",
    "Ete":         "",
    "As_calc_cm2": "cm²",
    "As_min_cm2":  "cm²",
    "As_req_cm2":  "cm²",
}
resultado = calcular_armadura_flexion(fc, fy, b, d, Mn, beta1)
for k, v in resultado.items():
    if k != "opciones":
        u = unidades_flex.get(k, "")
        print(f"  {k}: {v} {u}".strip())

# Opciones de armadura
print("\n=== OPCIONES DE ARMADURA ===")
if "opciones" in resultado:
    for op in resultado["opciones"]:
        print(f"  Φ{op['ds_mm']} x {op['n_barras']} barras | "
              f"As={op['As_real_cm2']} cm² | "
              f"sep={op['separacion_cm']} cm | "
              f"Md={op['Md_kNm']} kN·m | "
              f"peso={op['peso_kg_m']} kg/m")