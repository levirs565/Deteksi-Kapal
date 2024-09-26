from gpiozero import PWMOutputDevice
import time

# Pin definitions
PIN = 4  # GPIO 26 corresponds to physical pin 37


# Initialize PWM device with 50Hz frequency
# our optimal frequentcy is 10Hz but it change to 50 the best setting is 70
motor = PWMOutputDevice(PIN, frequency=70)

def set_motor_speed(duty_cycle):
    """Sets the motor speed with the given duty cycle (0.0 to 1.0)."""
    motor.value = duty_cycle / 1000  # Convert percentage to a value between 0 and 1
    print(f"Set motor speed to {duty_cycle}%")

try:
    
    print("is passed?")
    set_motor_speed(70)
    time.sleep(10)

except KeyboardInterrupt:
    pass
finally:
    motor.value = 0  # Stop PWM
    print("GPIO cleaned up.")
