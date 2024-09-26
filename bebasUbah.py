from gpiozero import PWMOutputDevice
import time

# Pin definitions
PIN2 = 23  # GPIO pin for the first ESC control
PIN1 = 4   # GPIO pin for the second ESC control

# Initialize PWM devices with a higher frequency (e.g., 400 Hz)
# Inisialisasi motor dengan frekuensi 50 Hz
motor1 = PWMOutputDevice(PIN1, frequency=50)
# motor1 = Motor(PIN1)
# motor1.run(90)
motor2 = PWMOutputDevice(PIN2, frequency=50)
print("waiting for connect")
# Tunggu selama 5 detik
time.sleep(10)

# Ubah frekuensi motor menjadi 400 Hz
motor1.frequency = 400
motor2.frequency = 400


def set_motor_speed(duty_cycle1, duty_cycle2):
    """Sets the speeds of both motors with the given duty cycles (0.0 to 1.0)."""
    motor1.value = duty_cycle1 / 100  # Convert percentage to a value between 0 and 1 for motor1
    motor2.value = duty_cycle2 / 100  # Convert percentage to a value between 0 and 1 for motor2
    print(f"Set motor speeds to Motor1: {duty_cycle1}%, Motor2: {duty_cycle2}%")

try:
    print("Starting motors...")
    duty_cycle1 = 90  # Start at 90% for motor1
    duty_cycle2 = 5.0  # Start at 90% for motor2
    set_motor_speed(duty_cycle1, duty_cycle2)

    while duty_cycle1 >= 0 or duty_cycle2 >= 0:
        time.sleep(1)  # Wait for 1 second
        
        if duty_cycle1 > 1:
            duty_cycle1 -= 1  # Decrease motor1 speed by 1%
        else:
            duty_cycle1 = 0  # Finally set motor1 to 0%
        
        if duty_cycle2 > 1:
            duty_cycle2 -= 1  # Decrease motor2 speed by 1%
        else:
            duty_cycle2 = 0  # Finally set motor2 to 0%
        
        set_motor_speed(duty_cycle1, duty_cycle2)

except KeyboardInterrupt:
    pass
finally:
    motor1.value = 0  # Stop PWM for motor1
    motor2.value = 0  # Stop PWM for motor2
    print("GPIO cleaned up.")
