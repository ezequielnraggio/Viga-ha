from calculos.cargas import calcular_cargas
from calculos.corte import calcular_armadura_corte

# Datos
Qd = 12
Qs = 8
L  = 7
fc = 30
fy = 420
b  = 0.30
d  = 0.56

cargas = calcular_cargas(Qd, Qs, L)
qu = cargas["qu"]

print("=== CARGAS CORTE ===")
print(f"  qu:      {qu} kN/m")
print(f"  Vu(x=d): {round(qu * (L/2 - d), 2)} kN")

print("\n=== CORTE ===")
resultado = calcular_armadura_corte(fc, fy, b, d, qu, L)
for k, v in resultado.items():
    if k != "opciones":
        print(f"  {k}: {v}")

print("\n=== OPCIONES DE ESTRIBOS ===")
if "opciones" in resultado:
    for op in resultado["opciones"]:
        print(f"  Φ{op['db_mm']} c/{op['s_adopt_cm']}cm | "
              f"Av/s={op['Av_s_cm2m']} cm²/m | "
              f"Avmin/s={op['Avmin_s_cm2m']} cm²/m | "
              f"Vd={op['Vd_kN']} kN | "
              f"peso={op['peso_kg_m']} kg/m")