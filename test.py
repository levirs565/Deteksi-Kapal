import RPi.GPIO as GPIO
import time

# Constants
ESC_PIN = 4  # GPIO pin connected to the ESC
MIN_PWM = 1401  # Minimum pulse width (in microseconds)
MAX_PWM = 2200  # Maximum pulse width (in microseconds)
FREQUENCY = 50  # PWM frequency in Hertz

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(ESC_PIN, GPIO.OUT)

# Create a PWM instance
pwm = GPIO.PWM(ESC_PIN, FREQUENCY)
pwm.start(0)
 # Start PWM with 0% duty cycle
 
def init():
    duty_cycle = 800 / 20000 * 100  # Convert to duty cycle

    # Change the PWM signal
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(2)

def set_esc_speed(speed):
    """Set ESC speed between 0 (stopped) and 100 (full speed)."""
    if speed < 0 or speed > 100:
        raise ValueError("Speed must be between 0 and 100.")

    # Calculate the pulse width
    pulse_width = MIN_PWM + (speed / 100) * (MAX_PWM - MIN_PWM)
    duty_cycle = pulse_width / 20000 * 100  # Convert to duty cycle

    # Change the PWM signal
    pwm.ChangeDutyCycle(duty_cycle)

try:
    # Initialize ESC (usually you need to send a maximum signal to initialize)
    init()
    set_esc_speed(100)  # Set to max speed for initialization
    time.sleep(2)  # Wait for 2 seconds

    # Set speed (example: 50% throttle)
    set_esc_speed(50)
    time.sleep(5)  # Run for 5 seconds

    # Set speed to 0% (stop)
    set_esc_speed(0)

finally:
    # Cleanup
    pwm.stop()
    GPIO.cleanup()
