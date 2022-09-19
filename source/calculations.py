
import math
from constants import coxa_len, length_side, y_start, y_step, x_range
from constants import tibia_len
from constants import femur_len

temp_a = math.sqrt(pow(2 * x_range + length_side, 2) + pow(y_step, 2))
temp_b = 2 * (y_start + y_step) + length_side
temp_c = math.sqrt(pow(2 * x_range + length_side, 2) + pow(2 * y_start + y_step + length_side, 2))
temp_alpha = math.acos((pow(temp_a, 2) + pow(temp_b, 2) - pow(temp_c, 2)) / 2 / temp_a / temp_b)

# site for turn
turn_x1 = (temp_a - length_side) / 2
turn_y1 = y_start + y_step / 2
turn_x0 = turn_x1 - temp_b * math.cos(temp_alpha)
turn_y0 = temp_b * math.sin(temp_alpha) - turn_y1 - length_side

def cartesian_to_polar(x, y, z):
    '''
        Convert Cartesian (x,y,z) Coordinates to Polar Coordinates (angle, hypotenuse)
    '''
    # signValue = 1 if (x >= 0) else -1
    # w = signValue * math.sqrt(pow(x, 2) + pow(y, 2))

    if x >= 0: #change to value_if_true if condition else value_if_false
        w = math.sqrt(pow(x, 2) + pow(y, 2))
    else:
        w = -1 * (math.sqrt(pow(x, 2) + pow(y, 2)))

    v = w - coxa_len
    alpha_tmp = (pow(femur_len, 2) - pow(tibia_len, 2) + pow(v, 2) + pow(z, 2)) / 2 / femur_len / math.sqrt(
        pow(v, 2) + pow(z, 2))

    if alpha_tmp > 1 or alpha_tmp < -1:
        if alpha_tmp > 1:
            alpha_tmp = 1
        else:
            alpha_tmp = -1

        # alpha_tmp = 1 if (alpha_tmp > 1) else alpha_tmp = -1

    alpha = math.atan2(z, v) + math.acos(alpha_tmp)

    beta_tmp = (pow(femur_len, 2) + pow(tibia_len, 2) - pow(v, 2) - pow(z, 2)) / 2 / femur_len / tibia_len

    if beta_tmp > 1 or beta_tmp < -1:
        if beta_tmp > 1:
            beta_tmp = 1
        else:
            beta_tmp = -1

    beta = math.acos(beta_tmp)
    # state = "nice" if is_nice else "not nice"
    # gamma = math.atan2(y, x) if (w >= 0) else math.atan2(-y, -x)
    if w >= 0: #change to value_if_true if condition else value_if_false
        gamma = math.atan2(y, x)
    else:
        gamma = math.atan2(-y, -x)

    #trans degree pi->180
    alpha = alpha / math.pi * 180
    beta = beta / math.pi * 180
    gamma = gamma / math.pi * 180

    return (alpha, beta, gamma)
