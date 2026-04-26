import math

def calcular_cargas(Qd, Qs, L):
    """
    Calcula cargas últimas y solicitaciones de flexión y corte.
    Qd: carga muerta (kN/m)
    Qs: sobrecarga (kN/m)
    L: luz de la viga (m)
    Retorna dict con qu, Mu, Mn, Vu_max, Vn.
    """
    # Combinaciones ELU - CIRSOC 201
    ELU1 = 1.4 * Qd
    ELU2 = 1.2 * Qd + 1.6 * Qs
    qu = max(ELU1, ELU2)

    # Solicitaciones flexión
    Mu = qu * L**2 / 8 / 1000    # MN·m
    Mn = Mu / 0.9                 # MN·m

    # Solicitaciones corte
    Vu_max = qu * L / 2           # kN (en el apoyo)
    Vn = Vu_max / 0.75            # kN (cortante nominal)

    return {
        "ELU1":    round(ELU1, 2),
        "ELU2":    round(ELU2, 2),
        "qu":      round(qu, 2),
        "Mu":      round(Mu, 4),
        "Mn":      round(Mn, 4),
        "Vu_max":  round(Vu_max, 2),
        "Vn":      round(Vn, 2),
    }