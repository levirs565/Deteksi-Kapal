from gpiozero import PWMOutputDevice
import time

class Motor:
		def __init__(self, pin):
			self.pin = pin
			self.motor = PWMOutputDevice(pin, frequency=400)
			self.set_throttle(800)
			time.sleep(2)
		def run(self, speed):
			self.set_throttle(speed)
		def stop(self):
			self.set_throttle(800)
			
			
		def set_throttle(self, ms):
			duty_cycle = ms / 20000
			self.motor.value = 1

motor1 = Motor(4)
motor1.run(1200)
while True:
	pass
