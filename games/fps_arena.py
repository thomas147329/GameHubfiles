import math
import sys
import pygame
pygame.init()
WIDTH, HEIGHT = 1280, 720
HALF_H = HEIGHT // 2
FOV = math.radians(70)
NUM_RAYS = 320
MAX_DEPTH = 28
MOVE_SPEED = 3.8
MOUSE_SENS = 0.0025
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Explorer - 3D Exploration")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24, bold=True)
big = pygame.font.SysFont("Arial", 52, bold=True)
MAP = [
    "111111111111111111","100000000000000001","101111011111110101",
    "100001000000010001","101101011111010101","100001010001000001",
    "111101010101111101","100001000100000001","101111110111110101",
    "100000000000000001","101111011111110101","100000010000010001",
    "101111010111010101","100000000001000001","111111111111111111",
]
MAP_W, MAP_H = len(MAP[0]), len(MAP)
player = [2.5, 1.8]
angle = 0.0
visited = set()
LANDMARKS = [(5.5,1.7,"Old Tower"),(12.5,3.5,"Forest Gate"),(4.5,9.5,"Hidden Garden"),(13.5,9.5,"Ancient Ruins"),(9.5,12.5,"Lost Camp")]

def wall_at(x,y):
    mx,my=int(x),int(y)
    return mx<0 or my<0 or mx>=MAP_W or my>=MAP_H or MAP[my][mx]=="1"

def move_player(dx,dy):
    nx,ny=player[0]+dx,player[1]+dy
    if not wall_at(nx,player[1]): player[0]=nx
    if not wall_at(player[0],ny): player[1]=ny

def angle_difference(a,b): return (a-b+math.pi)%(2*math.pi)-math.pi

def draw_world():
    screen.fill((100,155,205)); pygame.draw.rect(screen,(70,105,65),(0,HALF_H,WIDTH,HALF_H))
    zbuffer=[MAX_DEPTH]*NUM_RAYS; ray_width=WIDTH/NUM_RAYS
    for r in range(NUM_RAYS):
        ray_angle=angle-FOV/2+FOV*r/NUM_RAYS; ca,sa=math.cos(ray_angle),math.sin(ray_angle); depth=.05
        while depth<MAX_DEPTH:
            if wall_at(player[0]+ca*depth,player[1]+sa*depth): break
            depth+=.035
        corrected=max(depth*math.cos(ray_angle-angle),.001); zbuffer[r]=corrected
        h=min(HEIGHT*2,int(HEIGHT/corrected)); shade=max(45,min(205,int(210/(1+corrected*.10))))
        pygame.draw.rect(screen,(shade,min(210,shade+20),max(35,shade-25)),(int(r*ray_width),HALF_H-h//2,int(ray_width)+1,h))
    visible=[]
    for x,y,name in LANDMARKS:
        d=math.hypot(x-player[0],y-player[1]); rel=angle_difference(math.atan2(y-player[1],x-player[0]),angle)
        if abs(rel)<FOV*.65: visible.append((d,rel,x,y,name))
    visible.sort(reverse=True)
    for d,rel,x,y,name in visible:
        corrected=d*math.cos(rel)
        if corrected<=.1: continue
        sx=WIDTH/2+math.tan(rel)/math.tan(FOV/2)*WIDTH/2; size=max(12,min(180,int(HEIGHT/corrected*.45))); ray=int(sx/WIDTH*NUM_RAYS)
        if 0<=ray<NUM_RAYS and corrected<zbuffer[ray]+.4:
            left,top=int(sx-size/2),int(HALF_H-size*.8)
            pygame.draw.rect(screen,(225,190,65),(left,top,size,size),border_radius=6)
            pygame.draw.rect(screen,(75,55,30),(left+size//3,top+size//3,size//3,size//2))
            label=font.render(name,True,(255,255,255)); screen.blit(label,(left,top-label.get_height()-4))

def update_landmarks():
    for i,(x,y,name) in enumerate(LANDMARKS):
        if math.hypot(player[0]-x,player[1]-y)<1.0: visited.add(i)

def draw_hud():
    pygame.draw.rect(screen,(15,25,25),(18,18,470,110),border_radius=10)
    screen.blit(font.render("EXPLORER",True,(255,255,255)),(32,28))
    screen.blit(font.render(f"Landmarks discovered: {len(visited)}/{len(LANDMARKS)}",True,(230,230,210)),(32,60))
    screen.blit(font.render("WASD: move   Mouse: look   ESC: quit",True,(220,220,220)),(32,92))
    cx,cy=WIDTH//2,HEIGHT//2; pygame.draw.circle(screen,(255,255,255),(cx,cy),3)
    for label,target in [("N",0),("E",math.pi/2),("S",math.pi),("W",-math.pi/2)]:
        diff=angle_difference(target,angle)
        if abs(diff)<FOV/2: screen.blit(font.render(label,True,(255,255,255)),(int(WIDTH/2+diff/(FOV/2)*200),18))

def main():
    global angle
    pygame.event.set_grab(True); pygame.mouse.set_visible(False); running=True
    while running:
        dt=min(clock.tick(60)/1000,.05)
        for event in pygame.event.get():
            if event.type==pygame.QUIT: running=False
            elif event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: running=False
            elif event.type==pygame.MOUSEMOTION: angle+=event.rel[0]*MOUSE_SENS
        keys=pygame.key.get_pressed(); forward=int(keys[pygame.K_w])-int(keys[pygame.K_s]); strafe=int(keys[pygame.K_d])-int(keys[pygame.K_a]); length=math.hypot(forward,strafe)
        if length:
            forward/=length; strafe/=length
            move_player((math.cos(angle)*forward-math.sin(angle)*strafe)*MOVE_SPEED*dt,(math.sin(angle)*forward+math.cos(angle)*strafe)*MOVE_SPEED*dt)
        update_landmarks(); draw_world(); draw_hud()
        if len(visited)==len(LANDMARKS): screen.blit(big.render("EXPEDITION COMPLETE!",True,(255,255,255)),(WIDTH//2-280,HEIGHT-120))
        pygame.display.flip()
    pygame.mouse.set_visible(True); pygame.event.set_grab(False); pygame.quit(); sys.exit()
if __name__=="__main__": main()
