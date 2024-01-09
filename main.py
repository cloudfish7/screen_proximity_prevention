from machine import Pin, I2C, PWM
import framebuf,sys,utime,machine,network
from vl53l0x import VL53L0X

# variable
LIMIT_DISTANCE = 60
CHECK_INTERVAL = 3
SDA_PIN = 8
SCL_PIN = 9
BUZZER_GPIO = 17

def get_default_led_gpio():
	# if this hardware is  raspberry pi Pico W
	if hasattr(network, "WLAN"):
		return "LED" 
	
	return "25"

# notify health status with led
def health_status(error_code, DEFAULT_LED_GPIO=25):

	DEFAULT_LED_GPIO = get_default_led_gpio()
	led = Pin(DEFAULT_LED_GPIO, Pin.OUT)
	led.off()

	# No Error 
	if error_code == 0:
		led.on()
	# Error Distance Sensor
	elif error_code == 1:
		
		while True:
			led.off()
			utime.sleep(1.5)
			led.on()
			utime.sleep(1.5)

	# Unknown Error
	elif error_code == 2:

		while True:
			led.off()
			utime.sleep(0.5)
			led.on()
			utime.sleep(0.5)


# ring buzzer
def alert():

	buzzer = PWM(Pin(BUZZER_GPIO))
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
		print(f"Execption: {e}")
		health_status(error_code=1)

	# status health
	health_status(error_code=0)

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
			print(f"Execption: {e}")
			health_status(error_code=2)

if __name__ == "__main__":
	main()