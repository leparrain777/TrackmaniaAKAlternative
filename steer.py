import vgamepad as vg
import time
from pynput.keyboard import Key, Listener

ACTIVATION_KEY = 'f'
# RESET_KEY = 'f'
LEFT = Key.left
RIGHT = Key.right
GAMEPAD_ATTEMPTS = 5

MAX_JOY = 32767
FPS = 100
TARGET = 1/FPS

def clip(v, l, h):
    if v < l:
        return l
    if v > h:
        return h
    return v

class KbSteer:
    gamepad = None
    leftPressed = False
    rightPressed = False
    activated = False
    steer = 0

    def onPress(self, key):
        try:
            if key.char == ACTIVATION_KEY:
                self.activated = True

        except AttributeError:
            if key == LEFT:
                self.leftPressed = True
            if key == RIGHT:
                self.rightPressed = True

    def onRelease(self, key):
        try:
            if key.char == ACTIVATION_KEY:
                self.activated = False

        except AttributeError:
            if key == LEFT:
                self.leftPressed = False
            if key == RIGHT:
                self.rightPressed = False

    decayrate = .90
    compdecayrate = 1-decayrate
    mode = False
    def attempt6_2Update(self):
        if not self.mode:
            if self.leftPressed and self.rightPressed and not self.mode:
                self.steer = 0    
            elif self.leftPressed and not self.mode: 
                self.steer = -1   
            elif self.rightPressed and not self.mode:
                self.steer = 1
            self.mode = True

        else :
            self.steer = self.decayrate*self.steer + (self.compdecayrate) * (-self.leftPressed+self.rightPressed)
    
    def defaultUpdate(self):
        self.mode = False
        self.steer = -self.leftPressed+self.rightPressed
        
        

    def start(self):
        for _ in range(GAMEPAD_ATTEMPTS):
            try:
                self.gamepad = vg.VX360Gamepad()
                break
            except Exception as e:
                print(f"unable to connect gamepad, error <{e}>, retrying...")
                time.sleep(1)
        else:
            print("unable to connect to virtual gamepad after {GAMEPAD_ATTEMPTS} attempts, exiting")
        self.listener = Listener(
            on_press=self.onPress,
            on_release=self.onRelease
        )
        self.listener.start()

        while True:
            t = time.perf_counter()

            if self.activated:
                self.attempt6_2Update()
            else:
                self.defaultUpdate()
            # self.steer = clip(self.steer, -1.0, 1.0)
            self.gamepad.left_joystick(int(MAX_JOY * self.steer), 0)
            self.gamepad.update()
            # print(self.steer)

            delta = time.perf_counter() - t
            time.sleep(max(0, TARGET - delta))

kbsteer = KbSteer()
kbsteer.start()