import pygame,math,random
from perlin_noise import PerlinNoise as Pnoise
pygame.init()
screen_width=342
screen_height=174
info=pygame.display.Info()
window= pygame.display.set_mode((info.current_w,info.current_h-63),pygame.RESIZABLE)
screen=pygame.Surface((screen_width,screen_height)).convert()
pygame.display.set_caption("waves")
clock=pygame.time.Clock()
def get_noise(noise,size=[10,10]):
	return [[noise([x/size[0],y/size[1]]) for x in range(size[0])] for y in range(size[1])]
def get_dist(p1,p2):
	return ((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)**0.5
def withscroll(pos):
	return [(pos[0]-game.scroll[0]),(pos[1]-game.scroll[1])]
class types():
	def __init__(self):
		self.grass=1
		self.air=0
t=types()
class c():
	def __init__(self):
		self.key={
		"w":False,
		"a":False,
		"s":False,
		"d":False
		}
		self.otherkey={
		"e":False
		}
	def update(self):
		
		key=pygame.key.get_pressed()
		for k in self.key:
			self.key[k]=key[getattr(pygame,f"K_{k}")]
		for k in self.otherkey:
			self.otherkey[k]=key[getattr(pygame,f"K_{k}")]
c=c()
def get_surf_from_sheet(sheet,sheetpos,size):
	s=pygame.Surface(size,pygame.SRCALPHA).convert_alpha()
	s.fill((0,0,0,0))
	s.blit(sheet,sheetpos)
	return s
imgs={
	"tilesheet":pygame.image.load("imgs/tiles.png").convert_alpha(),
	"text":pygame.image.load("imgs/text.png").convert_alpha(),
	"player":pygame.image.load("imgs/petrov.png").convert_alpha()
}
class animation():
	def __init__(self,image,size:list,delay:int,frame=0):
		self.delay=delay
		self.timer=0
		self.frames=image
		self.frame=frame
		self.size=size
		self.img=pygame.Surface(size,pygame.SRCALPHA)
		self.img.fill((0,0,0,0))
		if type(image) in [list,tuple]:
			for itemv in image:
				if type(itemv) is not pygame.Surface:
					raise ValueError("image list/tuple contains non pygame.Surface object(s)")
			self.type="list"
			self.frames_amount=len(self.frames)
		elif type(image) is pygame.Surface:
			self.img.blit(self.frames)
			self.type="sheet"
			length=self.frames.get_width()
			self.frames_amount=length/self.size[0]
		else:
			raise ValueError("argument, image, is not a pygame.Surface or list object")
	def update(self):
		self.timer+=1
		if self.timer>=self.delay:
			if self.type=="sheet":
				self.timer=0
				self.frame+=1
				self.frame%=self.frames_amount
				self.img.fill((0,0,0,0))
				self.img.blit(self.frames,(self.frame*-self.size[0],0))			
			else:
				self.timer=0
				self.frame+=1
				self.frame%=self.frames_amount
				self.img.fill((0,0,0,0))
				self.img.blit(self.frames[frame],(0,0))			
	def draw(self,pos=(0,0)):
		screen.blit(self.img,pos)
	def jumpto(self,frame):
		self.frame=frame
		self.frame%=self.frames_amount+1
		self.img.fill((0,0,0,0))
		self.img.blit(self.frames,(self.frame*-self.size[0],0))

class text():
    def __init__(self):
        self.letters=["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","1","2","3","4","5","6","7","8","9","0",".","!",",","?","+","-","'","[","]",":","/","%"]
    def render(self,text,letter_size=[6,5],sheet=imgs["text"]):
        digit=-1
        textsurf=pygame.Surface((len(text)*letter_size[0],letter_size[1]),flags=pygame.SRCALPHA).convert_alpha()
        img=pygame.Surface((letter_size[0],letter_size[1]),flags=pygame.SRCALPHA).convert_alpha()
        for letter in text:
            digit+=1
            try:
                frame=self.letters.index(letter)
            except ValueError:
                frame=-1
            img.fill((0,0,0,0))
            img.blit(sheet,((1-(frame*letter_size[0])),0))
            textsurf.blit(img,(digit*letter_size[0],0))
        return textsurf
text=text()
class Tile():
	def __init__(self,img,pos,sheetpos=(0,0),lists=[]):
		self.img=get_surf_from_sheet(img,sheetpos,(16,16))
		self.pos=pos
		self.rect=self.img.get_rect(topleft=self.pos)
		for list_ in lists:
			list_.append(self)
	def draw(self):
		screen.blit(self.img,withscroll(self.pos))
class World():
	def __init__(self):
		self.bignoise=Pnoise(octaves=12,seed=round(random.random()*10000000))
		self.noise=Pnoise(octaves=35,seed=round(random.random()*10000000))
		self.finenoise=Pnoise(octaves=100,seed=round(random.random()*10000000))
		self.finemult=Pnoise(octaves=35,seed=round(random.random()*10000000))
		self.size=[screen_width,screen_height]
		self.limit=30
		self.map=pygame.Surface(self.size,pygame.SRCALPHA).convert_alpha()
		array=get_noise(self.noise,self.size)
		array2=get_noise(self.finenoise,self.size)
		array3=get_noise(self.finemult,self.size)
		array4=get_noise(self.bignoise,self.size)
		self.data=[[0 for x in range(self.size[0])] for y in range(self.size[1])]
		self.tiles=[[None for x in range(self.size[0])] for y in range(self.size[1])]
		self.tilelist=[]
		#make map
		for y,row in enumerate(array):
			for x,val in enumerate(row):
				#add=(max(max(self.size[0]/2+abs(x),self.size[1]/2+abs(y)),50+self.size[1]/2)-50-self.size[1]/2)/1000
				add=max(get_dist((self.size[0]/4,self.size[1]/2),(x/2,y))-self.limit,0)/150
				height=array4[y][x]*0.8+val+array2[y][x]*(array3[y][x]+0.7)+add
				if y==0 or y>=self.size[1]-1:
					continue
				elif x==0 or x>=self.size[0]-1:
					continue
				if -0.2>height:
					self.map.set_at((x,y),(10,220,80,255))
					self.data[y][x]=t.grass
				else:
					self.data[y][x]=t.air
		def check_sides(pos,val,sides=[None,None,None,None]):
						bools=[True for _ in range(4)]
						x=pos[0]
						y=pos[1]
						for i,side in enumerate(sides):
							if side==None:
								bools[i]=True
							else:
								if i==0:
									if self.data[y][x-1]==val:
										bools[i]=True if side==True else False
									else:
										bools[i]=True if side==False else False
								elif i==1:
									if self.data[y][x+1]==val:
										bools[i]=True if side==True else False
									else:
										bools[i]=True if side==False else False
								elif i==2:
									if self.data[y-1][x]==val:
										bools[i]=True if side==True else False
									else:
										bools[i]=True if side==False else False
								elif i==3:
									if self.data[y+1][x]==val:
										bools[i]=True if side==True else False
									else:
										bools[i]=True if side==False else False
						return False if False in bools else True
		for y,row in enumerate(self.data):
			for x,val in enumerate(row):
				data=self.data
				sheetpos=[0,0]
				
				if val==t.air:
					continue
				if data[y][x-1]==val and data[y][x+1]==val:					
					sheetpos[0]=-16
				elif data[y][x+1]==val:
					sheetpos[0]=0
				elif data[y][x-1]==val:
					sheetpos[0]=-32
				if data[y-1][x]==val and data[y+1][x]==val:
					sheetpos[1]=-16
				elif data[y+1][x]==val:
					sheetpos[1]=0
				elif data[y-1][x]==val:
					sheetpos[1]=-32
				if data[y][x-1]!=val and data[y][x+1]!=val and data[y-1][x]!=val and data[y+1][x]!=val:
					sheetpos=[0,-48]
				elif check_sides((x,y),val,[False,False,False,True]):
					sheetpos=[-32,-48]
				elif check_sides((x,y),val,[False,False,True,False]):
					sheetpos=[-32,-64]
				elif check_sides((x,y),val,[False,True,False,False]):
					sheetpos=[0,-64]
				elif check_sides((x,y),val,[True,False,False,False]):
					sheetpos=[-16,-64]
				elif check_sides((x,y),val,[True,True,False,False]):
					sheetpos=[-16,-48]
				elif check_sides((x,y),val,[False,False,True,True]):
					sheetpos=[0,-80]
				if val==t.grass:
					
					self.tiles[y][x]=Tile(imgs["tilesheet"],[x*16,y*16],sheetpos=sheetpos,lists=[self.tilelist])

				
		#place structs

		init_poses=[[random.random()*self.size[0],random.random()*self.size[1]] for _ in range(50)]
		def check_air(xy):
			if xy[1]+1>self.size[1] or xy[1]-1<0:
				return True
			else:
				return self.map.get_at((xy[0],xy[1]+1))[3]==0
		for pos in init_poses:
			if check_air(pos) or self.map.get_at(pos)[3]==255:
				count=0
				while check_air(pos) or self.map.get_at(pos)[3]==255:
					count+=1
					if count>1000:
						break
					if check_air(pos):
						pos[1]+=1
					elif self.map.get_at(pos)[3]==255:
						pos[1]-=1
					if pos[1]>self.size[1] or pos[1]<0:

						pos=[random.random()*self.size[0],random.random()*self.size[1]]
class Player():
	def __init__(self):
		self.img=animation(get_surf_from_sheet(imgs["player"],(-10,0),(40,13)),(10,13),12)
		self.disimg=self.img.img.copy()
		self.idle=get_surf_from_sheet(imgs["player"],(0,0),(10,13))
		self.pos=[game.world.size[0]*16/2,game.world.size[1]*16/2]
		self.speed=[0,0]
		self.fric=0.9
		self.accel=0.2
		self.jump_power=5
		self.grav=0.3
		self.moving=False
		self.grounded=False
		self.rect=self.img.img.get_rect()
		self.ground_line=(self.rect.bottomleft,self.rect.bottomright)
		self.bottom_tile=game.tiles[]
		#self.rect=pygame.Rect(self.pos,50,50)
	def update(self):
		if c.key["s"]:
			self.speed[1]+=self.accel
		if c.key["d"]:
			self.speed[0]+=self.accel
		if c.key["w"]:
			self.speed[1]-=self.accel
		if c.key["a"]:
			self.speed[0]-=self.accel
		self.moving=True if True in list(c.key.values()) else False
		self.speed[1]+=self.grav
		self.speed[0]*=self.fric
		self.speed[1]*=self.fric

		collidelist=game.world.tilelist
		self.pos[0]+=self.speed[0]
		self.rect.x=self.pos[0]
		if self.rect.collidelist(collidelist)!=-1:
			if self.speed[0]<0:
				for i in range(math.ceil(abs(self.speed[0]))):
					self.pos[0]+=1
					self.rect.x+=1
					if self.rect.collidelist(collidelist)==-1:
						break
			if self.speed[0]>0:
				for i in range(math.ceil(self.speed[0])):
					self.pos[0]-=1
					self.rect.x-=1
					if self.rect.collidelist(collidelist)==-1:
						break
			self.speed[0]=0

		self.pos[1]+=self.speed[1]
		self.rect.y=self.pos[1]
		self.ground_line=(self.rect.bottomleft,self.rect.bottomright)
		if self.rect.collidelist(collidelist)!=-1:
			if self.speed[1]<0:
				for i in range(math.ceil(abs(self.speed[1]))):
					self.pos[1]+=1
					self.rect.y+=1
					if self.rect.collidelist(collidelist)==-1:
						break
			if self.speed[1]>0:
				for i in range(math.ceil(self.speed[1])):
					self.pos[1]-=1
					self.rect.y-=1
					if self.rect.collidelist(collidelist)==-1:
						break
			self.speed[1]=0
		if self.moving:
			self.img.update()
			self.disimg=self.img.img
		else:
			self.img.jumpto(0)
			self.disimg=self.idle
		
		
		self.rect.topleft=self.pos
	def draw(self):
		screen.blit(self.disimg,withscroll(self.pos))
		#pygame.draw.rect(screen,(255,0,0),self.rect)
class Game():
	def __init__(self):
		global screen
		screen.blit(text.render("loading..."))
		screen=pygame.transform.scale(screen,window.get_size())
		window.blit(screen,(0,0))
		pygame.display.update()
		self.world=World()
		self.scroll=[0,0]
		self.stage="play"
	def initother(self):
		self.player=Player()


game=Game()
game.initother()
run= True
while run==True:
	screen=pygame.Surface((screen_width,screen_height)).convert()
	screen.fill((50,110,220))
	screen.blit(game.world.map)
	c.update()
	clock.tick(60)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type==pygame.KEYDOWN:
			if event.key==pygame.K_e:
				c.otherkey["e"]=True
	game.player.update()
	
	game.scroll=[game.player.pos[0]-screen_width/2+5,game.player.pos[1]-screen_height/2+7]
	game.player.draw()
	for y in range(math.floor(game.scroll[1]/16)-5,math.floor(game.scroll[1]/16)+15):
		
		for x in range(math.floor(game.scroll[0]/16)-5,math.floor(game.scroll[0]/16)+30):
			try:
				tile=game.world.tiles[y][x]
			except IndexError:
				continue
			if type(tile)==Tile:
				tile.draw()
	pygame.display.set_caption(f"scroll:{game.scroll} fps:{clock.get_fps()}")
	screen=pygame.transform.scale(screen,window.get_size())
	window.blit(screen,(0,0))
	pygame.display.update()
    
pygame.quit()
