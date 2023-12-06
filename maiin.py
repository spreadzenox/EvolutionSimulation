from curses import COLORS
from email.mime import base
from pyexpat.errors import XML_ERROR_MISPLACED_XML_PI
from tkinter import font
from button import Button
import pygame
import math
import random as rd
import copy
pygame.init()
global REPRODUCE_RATE
REPRODUCE_RATE=150
global BASE_ENERGY
BASE_ENERGY=10
global REPRODUCE_DISTANCE
REPRODUCE_DISTANCE=3
global MOOVE_SPEED
MOOVE_SPEED=1
global SCAN_RANGE
SCAN_RANGE=7
global MUTATION_RATE
MUTATION_RATE=0.13
global FOOD_RATE
FOOD_RATE=0.95
global RESET_FOOD_RATE
RESET_FOOD_RATE=0.01
global BLOB_RATE
BLOB_RATE= 1-FOOD_RATE
global SPAWN_RATE
SPAWN_RATE=0.7
global RESET_SPAWN_RATE
RESET_SPAWN_RATE=0.01
global TAILLE_GRID
TAILLE_GRID=150
#CAREFUL THE MAIN WINDOW HAVE TO BE A SQUARE
global WIDTH
global HEIGHT
WIDTH, HEIGHT =  700, 700
global WIDTH_info
global HEIGHT_info
WIDTH_info, HEIGHT_info =  300, 300
global CELL_SIZE
CELL_SIZE=HEIGHT/TAILLE_GRID

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
WIN_info = pygame.display.set_mode((WIDTH_info, HEIGHT_info))
pygame.display.set_caption("Evolution Simulation")

global COLOR
COLOR={
"WHITE" : (255, 255, 255),
"YELLOW" : (255, 255, 0),
"BLUE" : (100, 149, 237),
"RED" : (188, 39, 50),
"DARK_GREY" : (80, 78, 81)}


global FONT
FONT = pygame.font.SysFont("comicsans", 16)
global FONT_PETIT
FONT_PETIT = pygame.font.SysFont("comicsans", 8)

class Grid:
	def __init__(self) :
		self.grid=[[[] for i in range(TAILLE_GRID)] for j in range(TAILLE_GRID)]
		for i in range (TAILLE_GRID):
			for j in range(TAILLE_GRID):
				rd_spawn=rd.random()
				rd_type=rd.random()
				if rd_spawn<=SPAWN_RATE:
					if rd_type<=FOOD_RATE:
						self.grid[i][j].append(Food(i,j,rd.randint(1,8)))
					else:
						self.grid[i][j].append(Blob(i,j,BASE_ENERGY))
	def instantiate(self,entity):
		self.grid[entity.x][entity.y]=[entity]
	def reset_food(self):
		for i in range (TAILLE_GRID):
			for j in range(TAILLE_GRID):
				rd_spawn=rd.random()
				if rd_spawn<=RESET_FOOD_RATE:
					if self.grid[i][j] != []:
						if type(self.grid[i][j][0]) == Blob and self.grid[i][j][0].energy>0:
							self.grid[i][j][0].suicide()
					self.grid[i][j]=[Food(i,j,rd.randint(1,8))]
	def reset_spawn(self,brain):
		for i in range (TAILLE_GRID):
			for j in range(TAILLE_GRID):
				rd_spawn=rd.random()
				if rd_spawn<=RESET_SPAWN_RATE:
						self.grid[i][j]=[Blob(i,j,BASE_ENERGY,brain=brain)]
	def reset_map(self):
		self.grid=[[[] for i in range(TAILLE_GRID)] for j in range(TAILLE_GRID)]
		for i in range (TAILLE_GRID):
			for j in range(TAILLE_GRID):
				rd_spawn=rd.random()
				rd_type=rd.random()
				if rd_spawn<=SPAWN_RATE:
					if rd_type<=FOOD_RATE:
						self.grid[i][j].append(Food(i,j,rd.randint(1,8)))
					else:
						self.grid[i][j].append(Blob(i,j,BASE_ENERGY))
		
				
		
		
#FONCTION DE DISTANCE MODULO TAILLE_GRID
def distance(obj1,obj2):
	return(abs(dist_x(obj1,obj2))+abs(dist_y(obj1,obj2)))


#ATTENTION CES FONCTION DONNE LES MOUVEMENTS SUR X et Y A FAIRE POUR SOURCE POUR ALLER JUSQU'A DESTINATION
def dist_x(source,destination):
	absolute=abs((destination.x-source.x)%TAILLE_GRID)
	if absolute>TAILLE_GRID/2:
		return(-1*(absolute-TAILLE_GRID))
	else:
		return(absolute)

def dist_y(source,destination):
	absolute=abs((destination.y-source.y)%TAILLE_GRID)
	if absolute>TAILLE_GRID/2:
		return(-1*(absolute-TAILLE_GRID))
	else:
		return(absolute)

class Brain :
	def __init__(self,blob,input_size=7,output_size=6,n_layer=4) :
		self.weight=[[[rd.uniform(-1,1) for i in range(input_size)]for j in range (input_size)]for k in range(n_layer)]
		self.weight.append([[rd.uniform(-1,1) for i in range(input_size)]for j in range(output_size)])
		self.blob=blob
	def predict(self,entree):
		n_couche=1
		c_layer=entree
		for couche in self.weight:
			next_layer=[]
			for neurone in couche:
				c_value=0
				for i in range(len(neurone)):
					c_value+=neurone[i]*c_layer[i]
				next_layer.append(c_value)
			n_couche+=1
			if n_couche!=4:
				c_layer=next_layer
		return(next_layer)
					
		
		
		

class Food:
	def __init__(self, x ,y,amount):
		self.x=x
		self.y=y
		self.amount=amount
		self.color=(min(amount*30,255),0,0)
		self.radius=CELL_SIZE/8*amount/2
	def draw(self,win):
		x_pos=self.x*CELL_SIZE+CELL_SIZE/2
		y_pos=self.y*CELL_SIZE+CELL_SIZE/2
		pygame.draw.circle(win, self.color, (x_pos, y_pos), self.radius)
	def update(self):
		self.color=(min([self.amount*30,255]),0,0)
		self.radius=CELL_SIZE/8*self.amount/2
	def suicide(self):
		grid.grid[self.x][self.y]=[]
		
class BlobImage:
	def __init__(self, x, y,radius,color,blob):
		self.x = x
		self.y = y
		self.radius = radius
		self.color = color
		self.blob=blob
		blobs_images.append(self)
	
class Blob:
	TIMESTEP= 0.1
	def __init__(self, x, y, energy,brain=0,mutation_rate=0):
		self.x = x
		self.y = y
		x_real = self.x*CELL_SIZE+CELL_SIZE/2
		y_real = self.y*CELL_SIZE+CELL_SIZE/2
		self.radius = CELL_SIZE/2
		self.color = (0,min([energy*5,255]),max([0,255-energy*5]))
		self.energy = energy
		self.behaviour=[]
		self.fail=0
		self.image=BlobImage(color=self.color, x=x_real,y=y_real,radius=self.radius,blob=self)
		if mutation_rate==0:
			self.mutation_rate=MUTATION_RATE
		else:
			self.mutation_rate=mutation_rate
		if brain==0:
			self.brain= Brain(blob=self)
		else:
			self.brain=brain
			self.brain.blob=self
		blobs.append(self)

	def update(self):
		self.color=(0,min([self.energy*5,255]),max([0,255-self.energy*5]))
		self.radius = CELL_SIZE/2	
		self.image.color=self.color
		x_real = self.x*CELL_SIZE+CELL_SIZE/2
		y_real = self.y*CELL_SIZE+CELL_SIZE/2
		self.image.x=x_real
		self.image.y=y_real
		self.image.radius=self.radius

	def draw(self, win):
		x = self.x*CELL_SIZE+CELL_SIZE/2
		y = self.y*CELL_SIZE+CELL_SIZE/2
		if self.energy>0:
			pygame.draw.circle(win, self.color, (x, y), self.radius)	
	def scan_near_creatures(self):
		near_list=[]
		for i in range(-SCAN_RANGE,SCAN_RANGE):
			for j in range(-SCAN_RANGE,SCAN_RANGE):
				if abs(i)+abs(j)<=SCAN_RANGE:
					try:
						c=grid.grid[(self.x+i)%(TAILLE_GRID)][(self.y+j)%(TAILLE_GRID)]
						if c :
							if type(c[0]) is Blob:
								dist= abs(distance(self,c[0]))
								near_list.append((c[0],dist))
					except IndexError:
						pass		
		near_list.sort(key = lambda x: x[1])
		return (near_list)
	def scan_near_food(self):
		near_list=[]
		for i in range(-SCAN_RANGE,SCAN_RANGE):
			for j in range(-SCAN_RANGE,SCAN_RANGE):
				if abs(i)+abs(j)<=SCAN_RANGE:
						c=grid.grid[(self.x+i)%(TAILLE_GRID)][(self.y+j)%(TAILLE_GRID)]
						if c :
							if type(c[0]) is Food:
								dist= abs(distance(self,c[0]))
								near_list.append((c[0],dist))
		near_list.sort(key = lambda x: x[1])
		return (near_list)
	def moove(self,direction):
		self.energy-=1
		if direction == 1 and grid.grid[self.x][(self.y+MOOVE_SPEED)%(TAILLE_GRID)]==[]:
			self.y+=MOOVE_SPEED
			self.y=self.y%(TAILLE_GRID)
			self.fail=0
			return(0)
		elif direction ==2 and grid.grid[self.x][(self.y-MOOVE_SPEED)%(TAILLE_GRID)]==[]:
			self.y-=MOOVE_SPEED
			self.y=self.y%(TAILLE_GRID)
			self.fail=0
			return(0)
		elif direction ==3 and grid.grid[(self.x+MOOVE_SPEED)%(TAILLE_GRID)][self.y]==[]:
			self.x+=MOOVE_SPEED
			self.x=self.x%(TAILLE_GRID)
			self.fail=0
			return(0)
		elif direction ==4 and grid.grid[(self.x-MOOVE_SPEED)%(TAILLE_GRID)][self.y]==[]:
			self.x-=MOOVE_SPEED
			self.x=self.x%(TAILLE_GRID)
			self.fail=0
			return(0)
		else:
			return(1)
	
	def hit_closer(self):
		near_blob=self.scan_near_creatures()
		if near_blob ==[]:
			self.energy-=1
			return(1)
		closer_tuple = near_blob[0]
		if closer_tuple[1]<3:
			closer_tuple[0].energy-=closer_tuple[0].energy
			self.energy+=int(closer_tuple[0].energy*0.5)
		self.energy-=1
		self.fail=0
		return(0)
	def eat_closer(self) :
		near_food=self.scan_near_food()
		if near_food==[]:
			self.energy-=1
			return(1)
		for couple in near_food:
			if couple[1]<2:
				self.energy+=couple[0].amount
				couple[0].suicide()
				self.fail=0
				self.energy-=1
				return(0)
		self.energy-=1
		return(1)
	def reproduce(self):
		proba=self.energy/(4*BASE_ENERGY)
		random_truc=rd.random()
		if random_truc<=proba:
			x=rd.randint(0,1)
			if x==1:
				x=-REPRODUCE_DISTANCE
			elif x==0:
				x=REPRODUCE_DISTANCE
			y=rd.randint(0,1)
			if y==1:
				y=-REPRODUCE_DISTANCE
			elif y==0:
				y=REPRODUCE_DISTANCE
			interdit=list(range(0,REPRODUCE_DISTANCE))+list(range(TAILLE_GRID-REPRODUCE_DISTANCE,TAILLE_GRID))
			if self.x not in interdit and self.y not in interdit and self.energy>0 :
				if grid.grid[self.x+x][self.y+y] != [] and type(grid.grid[self.x+x][self.y+y])==Food :
					grid.grid[self.x+x][self.y+y][0].suicide()
				new_weights=copy.deepcopy(self.brain.weight)
				for couche in new_weights:
					for neurone in couche:
						for poid in neurone:
							if rd.random()<=self.mutation_rate:
								poid+=rd.gauss(0,1)*100*self.mutation_rate/(self.energy)
				new_brain=Brain(blob=self)
				new_brain.weight=new_weights
				if rd.random()<=self.mutation_rate:
					self.mutation_rate+=rd.gauss(0,0.3)*100*self.mutation_rate/(self.energy)
				new=Blob(x=self.x+x,y=self.y+y,energy=BASE_ENERGY,brain=new_brain,mutation_rate=self.mutation_rate)
				new.brain.blob=new
				grid.instantiate(new)
	def main(self):
		#SCAN
		near_food=self.scan_near_food()
		near_blob=self.scan_near_creatures()
		#TP BORDURE
		# if self.x==TAILLE_GRID-1:
		# 	if grid.grid[1][self.y]==[]:
		# 		self.x=1
		# 	if grid.grid[1][self.y]!=[] and type(grid.grid[1][self.y][0])==Food:
		# 		grid.grid[1][self.y][0].suicide()
		# 		self.x=1
		# if self.x==0:
		# 	if grid.grid[TAILLE_GRID-2][self.y]==[]:
		# 		self.x=TAILLE_GRID-2
		# 	if grid.grid[TAILLE_GRID-2][self.y]!=[] and type(grid.grid[TAILLE_GRID-2][self.y][0])==Food:
		# 		grid.grid[TAILLE_GRID-2][self.y][0].suicide()
		# 		self.x=TAILLE_GRID-2
		# if self.y==TAILLE_GRID-1:
		# 	if grid.grid[self.x][1]==[]:
		# 		self.y=1
		# 	if grid.grid[self.x][1]!=[] and type(grid.grid[self.x][1][0])==Food:
		# 		grid.grid[self.x][1][0].suicide()
		# 		self.y=1
		# if self.y==0:
		# 	if grid.grid[self.x][TAILLE_GRID-2]==[]:
		# 		self.y=TAILLE_GRID-2
		# 	if grid.grid[self.x][TAILLE_GRID-2]!=[] and type(grid.grid[self.x][TAILLE_GRID-2][0])==Food:
		# 		grid.grid[self.x][TAILLE_GRID-2][0].suicide()
		# 		self.y=TAILLE_GRID-2
		#CHOIX+ACTION
		if near_food==[]:
			closer_food_vector=[0,0,0]
		else :
			closer_food=near_food[0]
			closer_food_vector=[dist_x(self,closer_food[0]),dist_y(self,closer_food[0]),closer_food[0].amount]
		if near_blob ==[] :
			closer_blob_vector=[0,0,0,self.fail]
		else:
			closer_blob=near_blob[0]
			closer_blob_vector=[dist_x(self,closer_blob[0]),dist_y(self,closer_blob[0]),closer_blob[0].energy,self.fail]
		entree=closer_food_vector+closer_blob_vector
		result=self.brain.predict(entree)
		choice=result.index(max(result))
		self.consigne_behaviour(choice)
		if choice in [1,2,3,4]:
			self.fail+=self.moove(choice)
		if choice == 0:
			self.fail+=self.eat_closer()
		if choice == 5:
			self.fail+=self.hit_closer()
		if self.energy<=0:
			self.suicide()
	def consigne_behaviour(self,choice):
		if choice in [1,2,3,4]:
			if choice==1:
				self.behaviour.append("bas")
			if choice==2:
				self.behaviour.append("haut")
			if choice==3:
				self.behaviour.append("droite")
			if choice==4:
				self.behaviour.append("gauche")
		if choice == 0:
			self.behaviour.append("manger")
		if choice == 5:
			self.behaviour.append("taper")
	def main_behaviour(self):
		return(max(set(self.behaviour), key=self.behaviour.count))
	def behaviour_recap(self):
		manger=str(self.behaviour.count("manger"))
		taper=str(self.behaviour.count("taper"))
		bas=str(self.behaviour.count("bas"))
		droite=str(self.behaviour.count("droite"))
		haut=str(self.behaviour.count("haut"))
		gauche=str(self.behaviour.count("gauche"))
		return('bas= '+bas+' haut= '+haut+' droite= '+droite+' gauche= '+gauche+' taper= '+taper+' manger= '+manger)
	def suicide(self):
		grid.grid[self.x][self.y]=[]
		blobs.remove(self)
		blobs_images.remove(self.image)
			
		
		
	
				
		
			
			
			
		



def main():
	run = True
	clock = pygame.time.Clock()
	global blobs
	blobs=[]
	global blobs_images
	blobs_images=[]
	global grid
	grid=Grid()
	global turn
	turn=0
	extinc=0
	while True:
		while run:
			clock.tick(60)
			WIN.fill((0, 0, 0))
			WIN_info.fill((0, 0, 0))
			for i in range(TAILLE_GRID):
				#pygame.draw.line(WIN,width=1,start_pos=(HEIGHT/TAILLE_GRID*i,0),color=WHITE,end_pos=(HEIGHT/TAILLE_GRID*i,HEIGHT))
				for j in range (TAILLE_GRID):
					#pygame.draw.line(WIN,width=1,start_pos=(0,(HEIGHT/TAILLE_GRID)*j),color=WHITE,end_pos=(HEIGHT,(HEIGHT/TAILLE_GRID)*j))
					current_object=grid.grid[i][j]
					if current_object :
						current_object[0].update()
						current_object[0].draw(WIN)	
			for blob in blobs:
				blob.main()
			for blob in blobs_images:
				img = FONT_PETIT.render(str(blob.blob.energy), True, COLOR["WHITE"])
				WIN.blit(img, (blob.x, blob.y-10))
				mouse_pos = pygame.mouse.get_pos() # Or `pg.mouse.get_pos()`.
				# Calculate the x and y distances between the mouse and the center.
				dist_x = mouse_pos[0] - blob.x
				dist_y = mouse_pos[1] - blob.y
				# Calculate the length of the hypotenuse. If it's less than the
				# radius, the mouse collides with the circle.
				if math.hypot(dist_x, dist_y) < blob.radius:
					img = FONT.render("main = "+blob.blob.main_behaviour(), True, COLOR["WHITE"])
					WIN.blit(img, (blob.x, blob.y))
					img = FONT.render("last = "+blob.blob.behaviour[-1], True, COLOR["WHITE"])
					WIN.blit(img, (blob.x, blob.y+10))
					img = FONT.render(blob.blob.behaviour_recap(), True, COLOR["WHITE"])
					WIN.blit(img, (blob.x, blob.y+20))
							
			if turn%4==0 and turn!=0:
				grid.reset_food()
			if turn%(1000//REPRODUCE_RATE)==0 and turn!=0 :
				actual_blobs=copy.deepcopy(blobs)
				for blob in actual_blobs:
					blob.reproduce()
			print('TOUR NUMERO'+str(turn))
			print('Generation numero'+str(turn//(1000//REPRODUCE_RATE)))
			print('blobs en vie = ' +str(len(blobs)))
			print("extinction = "+str(extinc))
			if len(blobs)<=1:
				grid.reset_map()
				extinc+=1
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					run = False
			turn+=1
			pygame.display.update()

	pygame.quit()


main()
