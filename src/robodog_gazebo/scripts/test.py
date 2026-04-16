import math

# linkage dimensions (meters)
L = 0.179378082
lam = 0.180
l = 0.035
r = 0.035

M_TO_MM = 1000.0


def solve_geometry(theta_deg, L=L, lam=lam, l=l, r=r):
    """Solve the 4-bar linkage geometry. Returns (preferred_solution, all_solutions)."""

    theta = math.radians(theta_deg)

    d = math.sqrt(L**2 + r**2 + 2 * L * r * math.cos(theta))

    if not (abs(d - l) <= lam <= d + l):
        raise ValueError(
            f"No real solution: l={l}, lam={lam}, d={d:.6f} don't form a triangle."
        )

    alpha = math.atan2(-(L + r * math.cos(theta)), r * math.sin(theta))

    cos_beta = (l**2 + d**2 - lam**2) / (2 * l * d)
    cos_beta = max(-1.0, min(1.0, cos_beta))
    beta = math.acos(cos_beta)

    solutions = []

    for sign in (+1, -1):
        gamma = alpha + sign * beta

        lx_m = l * math.cos(gamma)
        ly_m = l * math.sin(gamma)

        lx_mm = lx_m * M_TO_MM
        ly_mm = ly_m * M_TO_MM

        cos_f = -ly_m / l
        cos_f = max(-1.0, min(1.0, cos_f))
        f_deg = math.degrees(math.acos(cos_f))

        solutions.append({
            "branch": "+beta" if sign == +1 else "-beta",
            "d_m": d,
            "lx_mm": lx_mm,
            "ly_mm": ly_mm,
            "f_deg": f_deg,
        })

    # pick the branch where top edge goes right and slightly down
    preferred = None
    for sol in solutions:
        if sol["lx_mm"] > 0 and sol["ly_mm"] < 0:
            preferred = sol
            break

    if preferred is None:
        preferred = solutions[0]

    return preferred, solutions


if __name__ == "__main__":
    theta = float(input("input theta in degrees: "))
    theta_deg = theta + 10.0

    preferred, all_solutions = solve_geometry(theta_deg)

    print(f"theta = {theta_deg:.6f} deg\n")

    print("Preferred solution:")
    print(f"  branch = {preferred['branch']}")
    print(f"  d      = {preferred['d_m']:.9f} m")
    print(f"  l_x    = {preferred['lx_mm']:.6f} mm")
    print(f"  l_y    = {-1 * preferred['ly_mm']:.6f} mm")
    print(f"  f      = {preferred['f_deg']:.6f} deg")

    print("\nAll branches:")
    for sol in all_solutions:
        print(f"  branch = {sol['branch']}")
        print(f"    l_x  = {sol['lx_mm']:.6f} mm")
        print(f"    l_y  = {-1 * sol['ly_mm']:.6f} mm")
        print(f"    f    = {sol['f_deg']:.6f} deg")