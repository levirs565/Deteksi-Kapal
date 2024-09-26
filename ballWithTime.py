from gpiozero import PWMOutputDevice
import time

# Pin definitions
PIN = 4  # GPIO 26 corresponds to physical pin 37

# Initialize PWM device with a higher frequency (e.g., 400 Hz)
motor = PWMOutputDevice(PIN, frequency=50)

def set_motor_speed(duty_cycle):
    """Sets the motor speed with the given duty cycle (0.0 to 1.0)."""
    motor.value = duty_cycle / 100  # Convert percentage to a value between 0 and 1
    print(f"Set motor speed to {duty_cycle}%")

try:
    print("Starting motor...")
    duty_cycle = 90  # Start at 90% saat 58 mati
    set_motor_speed(duty_cycle)

    while duty_cycle > 0:
        time.sleep(1)  # Wait for 1 second
        duty_cycle -= 5  # Decrease by 1%
        set_motor_speed(max(duty_cycle, 0))  # Ensure it doesn't go below 0%

except KeyboardInterrupt:
    pass
finally:
    motor.value = 0  # Stop PWM
    print("GPIO cleaned up.")
