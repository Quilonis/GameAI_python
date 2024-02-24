import pygame
from random import randint
import os
from time import sleep
import time

#Main settings
WIDTH = 700
HEIGHT = 700
FPS = 60

#Screen startUp
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gaem")
clock = pygame.time.Clock()


start_time=time.time()

class Area():
    #Object setUp
    def __init__(self,x,y,width,height,color=(255,0,0),way=None):
        
        self.rect = pygame.Rect(x,y,width,height)
        
        self.fill_color=color
        
        self.hit=0
        
        self.width=width
        self.height=height
        
        #Where object looking at , made for enemy's vision sticks
        self.way=way
    
    #Set color for rect
    def color(self,new_color):
        self.fill_color=new_color

    #Set outline for rect 
    def outline(self,frame_color,thickness):
        pygame.draw.rect(screen,frame_color,self.rect,thickness)
    
    #Check for collide ONE object
    def colliderect(self,rect):
        return self.rect.colliderect(rect)
    
    #Check for collide list of objects
    def collidelist(self,rect_list):
        return self.rect.collidelist(rect_list)

    #Draw rect
    def draw(self):
        pygame.draw.rect(screen, self.fill_color,self.rect)

    #Movement of player
    def player_movement(self,walls=[],speed=2):
        global end
        global enemies
        global escape
        
        keys = pygame.key.get_pressed()
        
        #check for collide with enemy
        if self.rect.collidelist(enemies) >= 0:
            print("game over")
            end = True
        #check for collide with exit zone
        if block1.collidelist(escape) >=0:
            print("you won!")
            end = True

        if keys[pygame.K_LEFT]:
            self.rect.x -= speed
            if self.rect.collidelist(walls) >= 0:
                self.rect.x += speed

        if keys[pygame.K_RIGHT]:
            self.rect.x += speed
            if self.rect.collidelist(walls) >= 0:
                self.rect.x -= speed

        if keys[pygame.K_UP]:
            self.rect.y -= speed
            if self.rect.collidelist(walls) >= 0:
                self.rect.y += speed

        if keys[pygame.K_DOWN]:
            self.rect.y += speed
            if self.rect.collidelist(walls) >= 0:
                self.rect.y -= speed

class Enemy(Area):
    def __init__(self,x,y,width,height,color=(255,0,0)):
        super().__init__(x,y,width,height,color)
    
        #Vision "Sticks" , making bot be able to see walls .
        
        #Horizontal sticks
        self.vision_rectHx=Area(x+25,y+5,width,height-10,(255,255,255),"right")
        self.vision_rectH=Area(x-25,y+5,width,height-10,(255,255,255),"left")
        
        #Vertical
        self.vision_rectV=Area(x+5,y-25,width-10,height,(255,255,255),"up")
        self.vision_rectVy=Area(x+5,y+25,width-10,height,(255,255,255),"down")

        #==================================================
        # Invisible box that aproaches player , if didn't collided to any of walls - Enemy will aproach player
        self.ghost_box = Area(x,y,15,15,(125,125,255))
        #Addition for ghost_box's functional
        self.run=0
        self.player_oldx=0
        self.player_oldy=0
        #===================================

        self.moving=True

        self.boxes=[self.vision_rectH,self.vision_rectHx,self.vision_rectV,self.vision_rectVy]

        #Own timer
        self.timer=-1
        #Where enemy block is looking to move
        self.way_move="right"
    
    #Find which of vision "sticks" are not colided to find way to move
    def find_collided(self):
        not_collided_boxes=[]
        for i in self.boxes:
            if i.hit == 0:
                not_collided_boxes.append(i)
        return not_collided_boxes

    #Draw hiden objects
    def draw_hiden(self):
        for i in self.boxes:
            i.draw()
        self.ghost_box.draw()
    

    def hiden_move(self):
        for i in self.boxes:
            if i.way=="up":
                i.rect.x=self.rect.x+5
                i.rect.y=self.rect.y-25
            if i.way=="down":
                i.rect.x=self.rect.x+5
                i.rect.y=self.rect.y+25
            if i.way=="left":
                i.rect.x=self.rect.x-25
                i.rect.y=self.rect.y+5
            if i.way=="right":
                i.rect.x=self.rect.x+25
                i.rect.y=self.rect.y+5

    #Ghost box movement , aproaches player and returns hit
    def find_player(self,player):
        if self.run==0:
            self.ghost_box.hit=0
            self.run=1
            self.ghost_box.rect.x=self.rect.x
            self.ghost_box.rect.y=self.rect.y
        
        #Using vectors to normalize movement

        try:
            direction = pygame.Vector2(player.rect.x - self.ghost_box.rect.x, player.rect.y - self.ghost_box.rect.y)
            direction = direction.normalize()

            speed = 20

            self.ghost_box.rect.x += direction.x * speed
            self.ghost_box.rect.y += direction.y * speed
        except:
            pass

        #Check for hit
        if self.ghost_box.collidelist(zones)>=0:
            self.ghost_box.hit=1
        if self.ghost_box.colliderect(player.rect):
            if self.ghost_box.hit==0:
                self.player_oldx=player.rect.x
                self.player_oldy=player.rect.y
            
            self.ghost_box.rect.x=self.rect.x
            self.ghost_box.rect.y=self.rect.y
            self.run=0
            return self.ghost_box.hit

    #Says where to move
    def go_to(self,x,y,walls=[]):
        
        #Vectors for normalizing movement
        direction = pygame.Vector2(x - self.rect.x , y - self.rect.y)
        direction = direction.normalize()
        speed = 3  

        self.rect.x += direction.x * speed
        self.rect.y += direction.y * speed
        #To prevent bugs(stucking in the wall) , checking for collide with wall . If collided , returns 1 and movement stops
        try:
            if self.rect.collidelist(walls)>=0:
                self.rect.x -= direction.x * speed
                self.rect.y -= direction.y * speed
                return 1
        except:
            pass

        #Checks if objects in approximate location +-10 blocks from taget position , also made to prevent stucking in blocks
        if self.rect.y >= y-10 and self.rect.y <= y+10 and self.rect.x >= x-10 and self.rect.x <= x+10:
            return 1
        #Returns 0 if object didn't collided or didn't get to the place , basically restarts that loop .
        else:
            return 0

    #Movement for object
    def move(self,target,walls=[]):
        
        self.hiden_move()

        inner_time=time.time()
        
        #If vision stick collides to wall hit takes number 1 , else 0
        for i in self.boxes:
            if i.rect.collidelist(walls)>=0:
                i.hit=1
            else:
                i.hit=0


        #Sets timer , if timer ends changes way of move , like: left,right,up,down,still
        if self.timer>int(inner_time)-int(start_time):
            pass
        else:
            self.timer=int(inner_time)-int(start_time)+5
            s=randint(0,5)
            if s == 5:
                self.way_move="still"
            else:
                try:
                    #Find not collided sticks and on that information chose way to move
                    go_to=self.find_collided()
                    self.way_move=go_to[randint(0,len(go_to)-1)].way
                    print("chaged way to: "+self.way_move)
                except:
                    self.way_move="right"
                    print("error1")

        #Finds player using ghost box
        self.find_player(target)
        if self.player_oldx != 0 and self.player_oldy != 0:
            r = self.go_to(self.player_oldx,self.player_oldy,walls)
            if r == 1:
                
                self.player_oldx=0
                self.player_oldy=0

                self.way_move="still"
                print("served")
        #Main movement
        elif self.way_move != "still":
            if self.moving==False:
                colli = self.find_collided()
                try:
                    self.way_move=colli[randint(0,len(colli)-1)].way
                except:
                    self.way_move="right"
                    print("error")

            if self.way_move=="right":
                self.rect.x+=2
                self.moving=True
                
                if self.rect.collidelist(walls)>=0:
                    self.rect.x-=2
                    self.moving=False
            
            if self.way_move=="left":
                self.rect.x-=2
                self.moving=True
                
                if self.rect.collidelist(walls)>=0:
                    self.rect.x+=2
                    self.moving=False
            
            if self.way_move=="up":
                self.rect.y-=2
                self.moving=True
                
                if self.rect.collidelist(walls)>=0:
                    self.rect.y+=2
                    self.moving=False
            
            if self.way_move=="down":
                self.rect.y+=2
                self.moving=True
                
                if self.rect.collidelist(walls)>=0:
                    self.rect.y-=2
                    self.moving=False
        else:
            self.moving = False





block1=Area(325,250,25,25,(255,255,255))
block2=Area(400,200,50,50)
block3=Area(200,300,50,50)


blocks=[block2,block3]


#Map=============================
map=[1,1,1,1,1,1,1,1,1,1,1,1,2,1,
     2,0,0,0,0,0,0,0,0,0,0,0,0,1,
     1,1,1,0,1,1,1,1,1,1,1,0,0,1,
     1,0,0,0,0,0,0,0,0,0,0,0,0,1,
     1,0,0,1,1,1,1,0,1,1,1,1,0,1,
     1,0,0,0,0,0,0,0,0,0,0,0,0,1,
     1,1,1,1,0,1,1,1,1,1,1,0,0,1,
     1,0,0,0,0,0,0,0,0,0,0,0,0,1,
     1,0,0,1,0,1,1,0,1,1,0,1,0,1,
     1,0,1,0,0,0,0,0,1,0,0,1,0,1,
     1,0,1,0,1,0,1,0,0,0,0,0,0,1,
     1,0,0,0,0,0,0,1,0,1,1,1,0,1,
     1,0,1,0,1,1,0,0,0,0,0,0,0,1,
     1,1,1,1,1,1,1,1,1,1,1,1,1,1]
#Map=============================

#Next block placement
xm=0
ym=0


zones=[]
escape=[]

if len(zones) != len(map):
    for block in map:
        if block==1:
            zones.append(Area(xm,ym,50,50,(0,100,0)))
            xm+=50
            if xm==700:
                ym+=50
                xm=0
        if block==2:
            zones.append(Area(xm,ym,50,50,(255,255,255)))
            escape.append(Area(xm,ym,60,60,(255,255,255)))
            xm+=50
            if xm==700:
                ym+=50
                xm=0
        if block==0:
            zones.append(Area(1000,1000,50,50,(0,0,0)))
            xm+=50
            if xm==700:
                ym+=50
                xm=0

# Main loop
end = False



#Generate enemies
enemies = []
for i in range(5):
    enemy = Enemy(350,75,25,25,(randint(10,255),randint(10,255),randint(10,255)))
    enemies.append(enemy)


while not end:
    #Draw objects
    screen.fill((0,0,0))
    block1.draw()
    block1.player_movement(zones)

    #Draw enemies
    for enemy in enemies:
        enemy.draw()
        enemy.move(block1,zones)

    #check for exit from game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            end = True

    #draw zones
    for s in zones:
        s.draw()
    
    # Update
    clock.tick(FPS)
    # display update
    pygame.display.update()

pygame.quit()
