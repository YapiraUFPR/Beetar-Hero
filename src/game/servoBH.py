from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)

servos = {
    "score_servo": {"channel": 7},
    "combo_servo_esq": {"channel": 11},
    "combo_servo_dir": {"channel": 15}
}

def create(servo_name, min_value, max_value, min_angle=0, max_angle=180):
    s = servos[servo_name]
    
    servo = kit.servo[s["channel"]]
    servo.set_pulse_width_range(500, 2500)
    servo.actuation_range = 180

    s["servo"] = servo
    s['min_value'] = min_value
    s['max_value'] = max_value
    s['min_angle'] = min_angle
    s['max_angle'] = max_angle

def set(servo_name, value):
    s = servos[servo_name]
    min_value = s['min_value']
    max_value = s['max_value']
    min_angle = s['min_angle']
    max_angle = s['max_angle']

    # limita o valor ao intervalo configurado
    value = max(min_value, min(value, max_value))

    # normalizacao de valor pra angulo
    ratio = (value - min_value) / (max_value - min_value)
    angle = min_angle + ratio*(max_angle - min_angle)
    print(servo_name, "value", value, "angle", angle)
    s["servo"].angle = angle

