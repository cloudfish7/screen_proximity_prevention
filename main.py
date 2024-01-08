from machine import Pin, I2C, PWM
import framebuf,sys,utime,machine
from vl53l0x import VL53L0X

# variable
LIMIT_DISTANCE = 60
CHECK_INTERVAL = 3
SDA_PIN = 8
SCL_PIN = 9
DEFAULT_LED_GPIO = 25
BUZZER_GPIO = 17

# notify health status with led
def health_status(error_code):

	led = Pin(DEFAULT_LED_GPIO, Pin.OUT)
	led.off()

	# No Error 
	if error_code == 0:
		led.on()
	# Error Distance Sensor
	elif error_code == 1:
		led.off()
		utime.sleep(2)
		led.on()
	# Unknown Error
	elif error_code == 2:
		led.off()
		utime.sleep(0.5)
		led.on()


# ring buzzer
def alert():

	buzzer = PWM(Pin(BUZZER_GPIO))
	#freqLis = [262, 294, 330, 349, 392, 440, 494, 523]
	freqLis = [523]
	for idx in range(0, len(freqLis)):
	    buzzer.freq(freqLis[idx])
	    buzzer.duty_u16(256*16)
	    utime.sleep(0.2)
	buzzer.duty_u16(0) 

	utime.sleep(3)

def main():
	sda = Pin(SDA_PIN)
	scl = Pin(SCL_PIN)
	id = 0
	#i2c = I2C(id=id, sda=sda, scl=scl, freq=400000)
	i2c = I2C(id=id, sda=sda, scl=scl)

	print("setting up i2c")
	print(i2c.scan())

	try:
		# Create a VL53L0X object------------------------------
		tof = VL53L0X(i2c)

		# the measuting_timing_budget is a value in ms, the longer the budget, the more accurate the reading.
		budget = tof.measurement_timing_budget_us
		print("Budget was:", budget)
		tof.set_measurement_timing_budget(40000)
	
		# tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 18)
		tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 12)

		# tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 14)
		tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 8)
	except Exception as e:
		health_status(1)

	# status health
	health_status(0)

	# Start ranging
	while True:
		utime.sleep(CHECK_INTERVAL)
		
		try:
			# Distance is acquired with one delay. so get distance two times with intention.
			distance = (tof.ping()-10)/10
			distance = (tof.ping()-10)/10

			# if someone 
			if distance < LIMIT_DISTANCE :
				print(str(distance)+"cm")
				alert()
			else:
				print(f"over {LIMIT_DISTANCE}cm")
		
		except Exception as e:
			health_status(2)

if __name__ == "__main__":
	main()