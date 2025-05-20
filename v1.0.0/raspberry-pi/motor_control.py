import RPi.GPIO as GPIO
import time

class MotorControl:
    def __init__(self):
        # 设置GPIO模式
        GPIO.setmode(GPIO.BCM)
        
        # 定义电机控制引脚
        self.motor_pins = {
            'left': {'forward': 17, 'backward': 18},
            'right': {'forward': 22, 'backward': 23}
        }
        
        # 初始化所有引脚
        for motor in self.motor_pins.values():
            for pin in motor.values():
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)

    def set_speed(self, left_speed, right_speed):
        # 控制左电机
        if left_speed > 0:
            GPIO.output(self.motor_pins['left']['forward'], GPIO.HIGH)
            GPIO.output(self.motor_pins['left']['backward'], GPIO.LOW)
        elif left_speed < 0:
            GPIO.output(self.motor_pins['left']['forward'], GPIO.LOW)
            GPIO.output(self.motor_pins['left']['backward'], GPIO.HIGH)
        else:
            GPIO.output(self.motor_pins['left']['forward'], GPIO.LOW)
            GPIO.output(self.motor_pins['left']['backward'], GPIO.LOW)

        # 控制右电机
        if right_speed > 0:
            GPIO.output(self.motor_pins['right']['forward'], GPIO.HIGH)
            GPIO.output(self.motor_pins['right']['backward'], GPIO.LOW)
        elif right_speed < 0:
            GPIO.output(self.motor_pins['right']['forward'], GPIO.LOW)
            GPIO.output(self.motor_pins['right']['backward'], GPIO.HIGH)
        else:
            GPIO.output(self.motor_pins['right']['forward'], GPIO.LOW)
            GPIO.output(self.motor_pins['right']['backward'], GPIO.LOW)

    def stop(self):
        for motor in self.motor_pins.values():
            for pin in motor.values():
                GPIO.output(pin, GPIO.LOW)

    def cleanup(self):
        self.stop()
        GPIO.cleanup() 