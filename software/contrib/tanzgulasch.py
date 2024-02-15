"""
 Tanzgulasch, every cool Eurorack needs a fancy name!

 Tanzgulasch started as a stupid idea of having some points bouncing around on the display.
 Collisions with the borders are generating triggers.
 The X and Y distances of the triangles center from the borders generate CVs.
 
 As it evolved I found it interesting enough to continue. See:
 
 https://www.youtube.com/watch?v=ojW_Fzyoauw
 
 
 WARNING: At the moment the script is a total mess!
 WARNING: I use a bigger display (128px by 64px) as the standard EuroPi!


din - random new triangle
ain - TODO: Speed? Or configurable effect?
k1 - depends on b2 (actual speed and scale (of CVs))
k2 - depends on b2
b1 - random new triangle
b2 - cycle through meaning of k1/k2
cv1 - Trigger at collision for point 1
cv2 - Trigger at collision for point 2
cv3 - Trigger at collision for point 3
cv4 - Distance of triangles center to x-origin
cv5 - Distance of triangles center to y-origin
cv6 - atm. median of cv4 and cv5. May change to some sqrt or log thing?

"""

"""
Todo

* speed: better use integer math?
* S/H Mode triggered by din?
* dx in "musikalischen" Verhältnis? e.g. 1/2 BPM 1/2 BPM (sinnvoll bei nur X etc)
* CV Out Skalierbar machen (kinda done)
* Menu "system" (idk if I use knobs.py the right way)
* more pythonesque code...
* save states

"""

from europi import *
from europi_script import EuroPiScript
import math
import time
from random import random
from experimental.knobs import KnobBank


TrigHV=7.0
TRIGMS=50
NUM_PARTS=const(3)
SCX=6.4
#SCY=6.4 # not needed here

gate=[cv1,cv2,cv3]
rung=[0,0,0]
odd=1
gdx = 0.5
gdy = 0.5
gsx = 0.5
gsy = 0.5


def rescale(x, old_min, old_max, new_min, new_max):
    if x <= old_min:
        return new_min
    elif x >= old_max:
        return new_max
    else:
        return (x - old_min) / (old_max - old_min) * (new_max - new_min) + new_min


class Particle:
    def __init__(self):
        self.snew()

    def snew(self):
        for i in range(NUM_PARTS):
            self.x = random()*10.0
            self.y = random()*10.0
            self.xa = self.x
            self.ya = self.y
            self.dx = random()-0.5#*k1.read_position() #*00.1
            self.dy = random()-0.5#*k2.read_position() #*00.1
#            print(self.dx,self.dy)


    def update(self, mygate):        
        global odd,gdx,gdy,gsx,gsy
        self.xa = self.x
        self.ya = self.y
    
        # some weigthed randomness so that it slowly drifts but does not get out of control?
        

        new_x = self.x + self.dx *gdx*0.01
        new_y = self.y + self.dy *gdy*0.01
#        print(gdx,gdy)

        if new_x >= 10.0 or new_x <= 0.0:
            gate[mygate].voltage(TrigHV)
            rung[mygate]=time.ticks_ms()
            self.dx=self.dx*-1
        else:
            self.x = new_x
            if time.ticks_diff(time.ticks_ms(), rung[mygate])>TRIGMS:
               gate[mygate].voltage(0)

        if new_y >= 10.0 or new_y <= 0.0:
            gate[mygate].voltage(TrigHV)
            rung[mygate]=time.ticks_ms()
            self.dy=self.dy*-1
        else:
            self.y = new_y
            if time.ticks_diff(time.ticks_ms(), rung[mygate])>TRIGMS:
               gate[mygate].voltage(0)


class Tanzgulasch(EuroPiScript):
    def __init__(self):
        super().__init__()
        state = self.load_state_json()

        # add some cool title :)
        oled.fill(0)
        oled.show()
       
        self.counter = state.get("counter", 0)
        self.enabled = state.get("enabled", True)

        self.particle=[]
        for i in range(NUM_PARTS):
            self.particle.append(Particle())

        self.request_next_k1 = False
        self.kb1 = (
            KnobBank.builder(k1)
            .with_locked_knob("dx", initial_percentage_value=gdx )
            .with_locked_knob("sx", initial_percentage_value=gsx)
            .build())          
        self.request_next_k2 = False
        self.kb2 = (
            KnobBank.builder(k2)
            .with_locked_knob("dy", initial_percentage_value=gdy )
            .with_locked_knob("sy", initial_percentage_value=gsy)
            .build())          


        @b2.handler_falling
        def request_next_k2_mode():
            self.request_next_k2 = True

        # ReInit
        @b1.handler_falling
        def button1():
            self.particle=[]
            for i in range(NUM_PARTS):
                self.particle.append(Particle())

        @din.handler
        def dinTrigger():
            self.particle=[]
            for i in range(NUM_PARTS):
                self.particle.append(Particle())
            
    def next_k_mode(self):
        self.kb1.next()
        self.request_next_k1 = False
        self.kb2.next()
        self.request_next_k2 = False

    def display_name(cls):
        return "Tanzgulasch"

    def toggle_enablement(self):
            self.enabled = not self.enabled
            self.save_state()

    def save_state(self):
        """Save the current state variables as JSON."""
        # Don't save if it has been less than 5 seconds since last save.
        if self.last_saved() < 5000:
            return

        state = {
            "counter": self.counter,
            "enabled": self.enabled,
        }
        self.save_state_json(state)


    def draw(self):
        global odd,gdx,gdy,gsx,gsy
        start = time.ticks_us()

#        oled.fill(0)
        oled.fill_rect(64,0,64,64,0)
        # update and set
        if 1:
            self.particle[0].update(0)
            x0 = 64+int(self.particle[0].x*SCX)
            y0 = int(self.particle[0].y*SCX)
            self.particle[1].update(1)
            x1 = 64+int(self.particle[1].x*SCX)
            y1 = int(self.particle[1].y*SCX)
            oled.line(x0,y0,x1,y1, 1)
            self.particle[2].update(2)
            x2 = 64+int(self.particle[2].x*SCX)
            y2 = int(self.particle[2].y*SCX)
            oled.line(x1,y1,x2,y2, 1)
            oled.line(x2,y2,x0,y0, 1)
        
        xs=(x0+x1+x2)//3
        ys=(y0+y1+y2)//3
        oled.vline(xs,0,4,2)
        oled.vline(xs,59,4,2)
        oled.vline(xs,ys-2,5,2)
        oled.hline(64,ys,4,2)
        oled.hline(123,ys,4,2)
        oled.hline(xs-2,ys,5,2)

        # Scale CV! Doto!
        vx = (xs-64)/64.0*gsx*10
        vy = (64-ys)/64.0*gsy*10
        vxy= (vx+vy)/2.0
#        vxy=math.sqrt(xs**2+ys**2)/256.0*10.0
        
        if odd>=4:
            odd=0
            oled.fill_rect(0,0,64,64,0)
            
            if self.kb1.current_name=="dx":
                gdx = self.kb1.dx.percent()*100
#                print(self.kb1.dx.percent())
                oled.text("Speed", 0, 0, 1)
                oled.text(self.kb1.current_name+f":{gdx:3.0f}", 0, CHAR_HEIGHT+4, 1)
                self.request_next_k1  = False             
#            if self.kb2.current_name=="dy":
                gdy = self.kb2.dy.percent()*100
                oled.text(self.kb2.current_name+f":{gdy:3.0f}", 0, CHAR_HEIGHT*2+5, 1)
                self.request_next_k2  = False             
            if self.kb1.current_name=="sx":
                gsx = self.kb1.sx.percent()
                oled.text("Scale", 0, 0, 1)
                oled.text(self.kb1.current_name+f":{gsx:1.2f}", 0,CHAR_HEIGHT+4, 1)
                self.request_next_k1  = False             
            if self.kb2.current_name=="sy":
                gsy = self.kb2.sy.percent()
                oled.text(self.kb2.current_name+f":{gsy:1.2f}", 0, CHAR_HEIGHT*2+5, 1)
                self.request_next_k2  = False             
           


# Frametimer
#        oled.text(f"{time.ticks_diff(time.ticks_us(), start)}" , 64, 4*CHAR_HEIGHT+1, 1)
#        oled.text(f"{self.particle[0].delta_t:0.2f}" , 0, 4*CHAR_HEIGHT+1, 1)
        odd=odd+1        
        oled.show()
#        print(vx,vy)
#        cv4.voltage(4.0)
        cv4.voltage(vx)
        cv5.voltage(vy)
        cv6.voltage(vxy)



    def main(self):
        while True:
            self.draw()
            if self.request_next_k2:
                self.next_k_mode()


if __name__ == "__main__":
    Tanzgulasch().main()

