import math

x_desired = 0.05
y_desired = -0.3
z_desired = 0.1

length_1A = 0.07134332
length_1B = 0.0154625
length_2 = 0.180
length_3 = 0.160

p = 1; # parity toggle

def inv_kin(x_desired, y_desired, z_desired, p):
    theta3 = p*math.acos((math.pow(x_desired - length_1A,2) + math.pow(y_desired,2) + math.pow(z_desired,2) - math.pow(length_1B,2) - math.pow(length_2,2) - math.pow(length_3,2))/(2*length_2*length_3))
    theta2 = math.atan2(x_desired-length_1A, math.sqrt(math.pow(y_desired,2) + math.pow(z_desired,2) - math.pow(length_1B,2))) - math.atan2(length_3*math.cos(theta3) + length_2, -length_3*math.sin(theta3)) + p*math.pi/2
    theta1 = math.atan2(z_desired,y_desired) - math.atan2(length_1B,-(length_3*math.cos(theta2 + theta3) + length_2*math.cos(theta2)))
    return [theta1,theta2,theta3]

print(inv_kin(x_desired,y_desired,z_desired,p))