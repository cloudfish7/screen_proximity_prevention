from machine import Pin, I2C, PWM
import framebuf,sys,time,utime,machine
from vl53l0x import VL53L0X

# variable
LIMIT_DISTANCE = 50
SDA_PIN = 8
SCL_PIN = 9
DEFAULT_LED_GPIO = 25
CHECK_INTERVAL = 3

# notify health status with led
def light_status(error_code):

	led = Pin(DEFAULT_LED_GPIO, Pin.OUT)
	led.off()

	# No Error 
	if error_code == 0:
		led.on()
	# Error Distance Sensor
	elif error_code == 1:
		led.off()
		time.sleep(2)
		led.on()

# ring buzzer
def alert():

	buzzer = PWM(Pin(17))
	#freqLis = [262, 294, 330, 349, 392, 440, 494, 523]
	freqLis = [523]
	for idx in range(0, len(freqLis)):
	    buzzer.freq(freqLis[idx])
	    buzzer.duty_u16(256*16)
	    time.sleep(0.2)
	buzzer.duty_u16(0) 

	time.sleep(3)

def main():
	sda = Pin(8)
	scl = Pin(9)
	id = 0
	i2c = I2C(id=id, sda=sda, scl=scl, freq=400000)

	print("setting up i2c")
	print(i2c.scan())

	try:
		# Create a VL53L0X object------------------------------
		tof = VL53L0X(i2c)

		# Pre: 12 to 18 (initialized to 14 by default)
		# Final: 8 to 14 (initialized to 10 by default)

		# the measuting_timing_budget is a value in ms, the longer the budget, the more accurate the reading.
		budget = tof.measurement_timing_budget_us
		print("Budget was:", budget)
		tof.set_measurement_timing_budget(40000)
	
		# Sets the VCSEL (vertical cavity surface emitting laser) pulse period for the
		# given period type (VL53L0X::VcselPeriodPreRange or VL53L0X::VcselPeriodFinalRange)
		# to the given value (in PCLKs). Longer periods increase the potential range of the sensor.
		# Valid values are (even numbers only):

		# tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 18)
		tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 12)

		# tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 14)
		tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 8)
	except Exception as e:
		light_status(1)

	# status health
	light_status(0)

	# Start ranging
	while True:
		utime.sleep(CHECK_INTERVAL)

		#can not measure over 50cm
		distance = (tof.ping()-10)/10
		# if someone 
		if distance < LIMIT_DISTANCE :
			print(str(distance)+"cm")
			alert()
		else:
			print(f"over {LIMIT_DISTANCE}cm")
		
if __name__ == "__main__":
	main()