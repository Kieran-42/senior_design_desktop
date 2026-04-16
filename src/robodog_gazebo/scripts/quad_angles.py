import math

def calculate_geometry(theta_input):
    L = 0.179375
    l = 0.035
    lam = 0.180
    r = 0.035
    
    phi_deg = 180 - theta_input
    phi_rad = math.radians(phi_deg)

    d = math.sqrt(L**2 + r**2 - 2 * L * r * math.cos(phi_rad))

    try:
        f_p1 = math.acos((L**2 + d**2 - r**2) / (2 * L * d))
        R_p1 = math.acos((r**2 + d**2 - L**2) / (2 * r * d))

        u_rad = math.acos((l**2 + lam**2 - d**2) / (2 * l * lam))
        
        f_p2 = math.acos((l**2 + d**2 - lam**2) / (2 * l * d))
        R_p2 = math.acos((lam**2 + d**2 - l**2) / (2 * lam * d))
        
        res_f = math.degrees(f_p1 + f_p2)
        res_u = math.degrees(u_rad)
        res_R = math.degrees(R_p1 + R_p2)
        print(f"phi: {phi_deg:.3f} degrees")
        print(f"f:   {res_f:.3f} degrees")
        print(f"u:   {res_u:.3f} degrees")
        print(f"R:   {res_R:.3f} degrees")
        print(f"sum of interior angles: {phi_deg + res_f + res_u + res_R:.3f} degrees")
        
    except ValueError:
        print("Invalid geometry for the given theta.")

def main():
    val = float(input("input theta in degrees: "))
    val = val - 10
    calculate_geometry(val)

if __name__ == "__main__":
    main()