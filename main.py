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
def add_poses(p1,p2):
	return (p1[0]+p2[0],p1[1]+p2[1])
def get_dist(p1,p2):
	return ((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)**0.5
def withoutscroll(pos):
	return [pos[0]+game.scroll[0],pos[1]+game.scroll[1]]
def withscroll(pos):
	return [(pos[0]-game.scroll[0]),(pos[1]-game.scroll[1])]
def make_surf(size,colour,alpha=0):
	surf=pygame.Surface(size,alpha).convert_alpha() if alpha==pygame.SRCALPHA else pygame.Surface(size,alpha).convert()
	surf.fill(colour)
	return surf
def make_circle_surf(radius,colour):
	surf=pygame.Surface([radius*2,radius*2],pygame.SRCALPHA).convert_alpha()
	surf.fill((0,0,0,0))
	pygame.draw.circle(surf,colour,(radius,radius),radius)
	return surf
def make_hole(surf,hole_surf,pos=(0,0))->pygame.Surface:
	mask=pygame.mask.from_surface(hole_surf)
	hole=mask.to_surface(setcolor=(255,255,255),unsetcolor=(0,0,0)).convert()
	hole.set_colorkey((0,0,0,0))
	surf.blit(hole,pos,special_flags=pygame.BLEND_RGB_SUB)
	return surf
def mouse_get_pos():
	x,y=pygame.mouse.get_pos()
	scale=[screen_width/window.get_width(),screen_height/window.get_height()]
	return [x*scale[0],y*scale[1]]
class types():
	def __init__(self):
		self.grass=1
		self.rock_tile=2
		self.air=0
t=types()
class c():
	def __init__(self):
		self.key={
		"w":False,
		"a":False,
		"s":False,
		"d":False,
		"SPACE":False
		}
		self.otherkey={
		"e":False
		}
		self.mouse={
			0:[False,False]
			}	
	def update(self):
		key=pygame.key.get_pressed()
		mouse=pygame.mouse.get_pressed()
		self.mouse[0][1]=self.mouse[0][0]
		self.mouse[0][0]=mouse[0]
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
	"player":pygame.image.load("imgs/petrov.png").convert_alpha(),
	"foliage_sheet":pygame.image.load("imgs/foliage.png").convert_alpha()
}
imgs.update({
	"wood_bridge":get_surf_from_sheet(imgs["tilesheet"],(0,-96),(16,16)),
	"small_rock":get_surf_from_sheet(imgs["foliage_sheet"],(0,-13),(14,8)),
	"rock":get_surf_from_sheet(imgs["foliage_sheet"],(0,0),(22,13)),
	"rock_sheet":get_surf_from_sheet(imgs["tilesheet"],(-48,0),(48,96)),
	"small_tree":get_surf_from_sheet(imgs["foliage_sheet"],(-22,0),(11,12))
	})
class sinfx():
	def __init__(self,height,frequency,length,delay,colour,thickness=2,angle=45):
		self.height=height
		self.frequency=frequency
		self.length=length
		self.speed=delay
		self.colour=colour
		size=(length,height*3)
		points=[]
		self.imgs=[]
		for offset in range(math.ceil(1/frequency*math.pi*2)):
			points=[]
			img=pygame.Surface(size,pygame.SRCALPHA).convert_alpha()
			img.fill((0,0,0,0))
			for x in range(math.ceil(size[0])):
				points.append((x,math.sin((x+offset)*frequency)*height+height))

			pygame.draw.lines(img, colour, False, points, thickness)
			img=pygame.transform.rotate(img,angle)
			self.imgs.append(img)
		self.img=animation(self.imgs,self.imgs[0].get_size(),delay)
	def update(self):
		self.img.update()
	def draw(self,pos):
		self.img.draw((0,0))
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
				self.img.blit(self.frames[self.frame],(0,0))			
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
class decr():
	def __init__(self,img,pos,anchor="bottomleft",lists=[]):
		self.pos=list(pos)
		self.img=img
		

		try:
			self.rect=self.img.get_rect()
			self.size=self.img.get_size()
		except AttributeError:
			self.size=self.img.img.get_size()
			self.rect=self.img.img.get_rect()
		setattr(self.rect,anchor,self.pos)
		self.y_order=self.rect.midbottom[1]
		for list_ in lists:
			list_.append(self)
		
	def update(self):
		try:
			self.img.update()
		except AttributeError:
			pass
	def draw(self):

		try:
			screen.blit(self.img,withscroll((self.rect.topleft)))
		except TypeError:
			self.img.draw(withscroll((self.rect.topleft))) 
class Tile():
	def __init__(self,img,pos,sheetpos=(0,0),lists=[]):
		self.img=get_surf_from_sheet(img,sheetpos,(16,16))
		self.pos=pos
		self.rect=self.img.get_rect(topleft=self.pos)
		for list_ in lists:
			list_.append(self)
		self.mappos=[self.pos[0]/16,self.pos[1]/16]
	def draw(self):
		screen.blit(self.img,withscroll(self.pos))
class World():
	def __init__(self):
		def check_sides(pos,val=1,sides=[None,None,None,None]):
			bools=[True for _ in range(4)]
			x=pos[0]
			y=pos[1]
			for i,side in enumerate(sides):
				if side==None:
					bools[i]=True
				else:
					if i==0:
						if self.data[y][x-1]!=t.air:
							bools[i]=True if side==True else False
						else:
							bools[i]=True if side==False else False
					elif i==1:
						if self.data[y][x+1]!=t.air:
							bools[i]=True if side==True else False
						else:
							bools[i]=True if side==False else False
					elif i==2:
						if self.data[y-1][x]!=t.air:
							bools[i]=True if side==True else False
						else:
							bools[i]=True if side==False else False
					elif i==3:
						if self.data[y+1][x]!=t.air:
							bools[i]=True if side==True else False
						else:
							bools[i]=True if side==False else False
			return False if False in bools else True
		self.bignoise=Pnoise(octaves=12,seed=round(random.random()*10000000))
		self.noise=Pnoise(octaves=35,seed=round(random.random()*10000000))
		self.finenoise=Pnoise(octaves=100,seed=round(random.random()*10000000))
		self.finemult=Pnoise(octaves=35,seed=round(random.random()*10000000))
		self.rock_noise=Pnoise(octaves=12,seed=round(random.random()*10000000))
		self.size=[screen_width,screen_height]
		self.limit=50
		self.map=pygame.Surface(self.size,pygame.SRCALPHA).convert_alpha()
		self.cover=self.map.copy()
		self.cover.fill((239,207,124))
		self.cover.set_colorkey((0,0,0))
		array=get_noise(self.noise,self.size)
		array2=get_noise(self.finenoise,self.size)
		array3=get_noise(self.finemult,self.size)
		array4=get_noise(self.bignoise,self.size)
		rock_array=get_noise(self.rock_noise,self.size)
		self.data=[[0 for x in range(self.size[0])] for y in range(self.size[1])]
		self.tiles=[[None for x in range(self.size[0])] for y in range(self.size[1])]
		self.tilelist=[]
		self.derclist=[]
		#make map
		for y,row in enumerate(array):
			for x,val in enumerate(row):
				#add=(max(max(self.size[0]/2+abs(x),self.size[1]/2+abs(y)),50+self.size[1]/2)-50-self.size[1]/2)/1000
				add=max(get_dist((self.size[0]/4,self.size[1]/1.7),(x/2,y))-self.limit,0)/150
				height=array4[y][x]*0.8+val+array2[y][x]*(array3[y][x]+0.7)+add
				if y==0 or y>=self.size[1]-1:
					continue
				elif x==0 or x>=self.size[0]-1:
					continue
				if -0.2>height:
					if -0.3>rock_array[y][x]:
						self.data[y][x]=t.rock_tile
					else:
						self.data[y][x]=t.grass
				else:
					self.data[y][x]=t.air
		grass_pallete=((31,209,85),(29,196,101),(26,173,143))
		dirt_pallete=((174,97,62),(150,83,78),(127,70,78))
		rock_tile_pallete=((145,145,159),(137,133,125))
		top_rock_pallete=((168,167,131),(137,133,125))
		for y,row in enumerate(self.data):
			for x,val in enumerate(row):
				if check_sides((x,y),t.grass,[None,None,False,None]) and val in (t.grass,t.rock_tile):
					if val==t.grass:
						self.map.set_at((x,y),random.choice(grass_pallete))
					elif val==t.rock_tile:
						self.map.set_at((x,y),random.choice(top_rock_pallete))

				elif val==t.grass:
					self.map.set_at((x,y),random.choice(dirt_pallete))
				elif val==t.rock_tile:
					self.map.set_at((x,y),random.choice(rock_tile_pallete))

				data=self.data
				sheetpos=[0,0]
				
				if val==t.air:
					continue
				if data[y][x-1]!=t.air and data[y][x+1]!=t.air:					
					sheetpos[0]=-16
				elif data[y][x+1]!=t.air:
					sheetpos[0]=0
				elif data[y][x-1]!=t.air:
					sheetpos[0]=-32
				if data[y-1][x]!=t.air and data[y+1][x]!=t.air:
					sheetpos[1]=-16
				elif data[y+1][x]!=t.air:
					sheetpos[1]=0
				elif data[y-1][x]!=t.air:
					sheetpos[1]=-32
				if data[y][x-1]==t.air and data[y][x+1]==t.air and data[y-1][x]==t.air and data[y+1][x]==t.air:
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
				if val==t.rock_tile:
					self.tiles[y][x]=Tile(imgs["rock_sheet"],[x*16,y*16],sheetpos=sheetpos,lists=[self.tilelist])	
		#place structs
		rock_palletee=((103,98,85),(84,89,69),(119,101,86),(70,85,57))
		rock_init_poses=[[math.floor(random.random()*self.size[0]),math.floor(random.random()*self.size[1])] for _ in range(150)]
		def check_air(xy):
			if xy[1]+1>self.size[1] or xy[1]-1<0:
				return True
			else:
				try:
					return self.map.get_at((xy[0],xy[1]+1))[3]==0
				except IndexError:
					return True
		for pos in rock_init_poses:
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
				if random.random()<=0.5:

					decr(imgs["small_rock"],[pos[0]*16+2,pos[1]*16+10],anchor="topleft",lists=[self.derclist])
				else:
					decr(imgs["rock"],[pos[0]*16-3,pos[1]*16+5],anchor="topleft",lists=[self.derclist])

				self.map.set_at(pos,random.choice(rock_palletee))
class bullet():
	def __init__(self,pos,speed,angle,wave,parent=None):
		self.pos=pos
		self.speed=speed
		self.angle=math.radians(angle)
		self.wave=wave
		mask_surf=pygame.Surface(wave.size,pygame.SRCALPHA).convert_alpha()
		mask_surf=pygame.transform.rotate(mask_surf,angle)
		self.rect=mask_surf.get_rect(center=self.pos)
		self.mask=pygame.mask.from_surface(mask_surf)
		self.pop_timer=0
		self.parent=parent

class Player():
	def __init__(self):
		self.img=animation(get_surf_from_sheet(imgs["player"],(-10,0),(40,13)),(10,13),12)
		self.disimg=self.img.img.copy()
		self.idle=get_surf_from_sheet(imgs["player"],(0,0),(10,13))
		self.jump_img=get_surf_from_sheet(imgs["player"],(-50,0),(10,13))
		self.pos=[game.world.size[0]*16/2,game.world.size[1]*16/2]
		self.mappos=[0,0]
		self.speed=[0,0]
		self.fric=0.7
		self.airrest=0.99
		self.accel=0.5
		self.jump_power=6
		self.grav=0.25
		self.moving=False
		self.grounded=False
		self.jumped=False
		self.max_coyote=12
		self.coyote=0

		self.placing_bridge=False
		self.bridge_pos=[0,0]

		self.rect=self.img.img.get_rect()
		self.ground_line=(self.rect.bottomleft,self.rect.bottomright)
		self.bottom_tile=game.world.tiles[math.floor(self.pos[1]/16)][math.floor(self.pos[0]/16)]
		#self.rect=pygame.Rect(self.pos,50,50)
	def update(self):
		if c.key["s"]:
			self.speed[1]+=self.accel
		if c.key["d"]:
			self.speed[0]+=self.accel if self.grounded else self.accel/5
		if (c.key["w"] or c.key["SPACE"]) and (self.grounded or self.coyote<self.max_coyote) and (not self.jumped):
			self.speed[1]-=self.jump_power
			self.jumped=True
		if c.key["a"]:
			self.speed[0]-=self.accel if self.grounded else self.accel/5
		self.moving=True if True in list(c.key.values()) else False
		self.speed[1]+=self.grav
		if self.grounded:
			self.speed[0]*=self.fric
			self.coyote=0
		else:
			self.speed[0]*=self.airrest
			self.coyote+=1
		self.bridge_pos=(math.floor((mouse_get_pos()[0]+game.scroll[0])/16)*16,math.floor((mouse_get_pos()[1]+game.scroll[1])/16)*16)

		if self.placing_bridge:
			if c.mouse[0]==[True,False]:
				try:
					game.world.tiles[int(self.bridge_pos[1]/16)][int(self.bridge_pos[0]/16)]
				except IndexError:
					pass
				else:
					if game.world.tiles[int(self.bridge_pos[1]/16)][int(self.bridge_pos[0]/16)]==None:
						
						game.world.tiles[int(self.bridge_pos[1]/16)][int(self.bridge_pos[0]/16)]=Tile(imgs["wood_bridge"],self.bridge_pos,lists=[game.world.tilelist])
		self.speed[1]*=1 if (c.key["w"] or c.key["SPACE"]) and self.speed[1]<=0 else self.airrest*0.92
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
				self.jumped=False
				self.grounded=True

			else:
				self.grounded=False
			self.speed[1]=0
		else:
			self.grounded=False
		
		if self.jumped:
			self.disimg=self.jump_img
		elif self.moving:
			self.img.update()
			self.disimg=self.img.img
		else:
			self.img.jumpto(0)
			self.disimg=self.idle
		self.mappos=[math.floor(self.pos[0]/16),math.floor(self.pos[1]/16)]

		self.rect.topleft=self.pos
	def draw(self):
		if self.placing_bridge:
			screen.blit(imgs["wood_bridge"],withscroll(self.bridge_pos))
		screen.blit(self.disimg,withscroll((self.pos[0]-1,self.pos[1])))
		#pygame.draw.rect(screen,(255,0,0),self.rect)
class Game():
	def __init__(self):
		global screen
		screen.blit(text.render("loading..."),(1,1))
		screen.blit(text.render("do not worry if it says 'not responding'"),(1,8))
		screen=pygame.transform.scale(screen,window.get_size())
		window.blit(screen,(0,0))
		pygame.display.update()
		self.scroll=[0,0]
		self.stage="play"
	def initother(self):
		self.world=World()
		self.player=Player()
testsin=sinfx(7,0.5,32,3,(255,0,255))
game=Game()
game.initother()
run= True
while run==True:
	screen=pygame.Surface((screen_width,screen_height)).convert()
	screen.fill((50,110,220))
	c.update()
	clock.tick(60)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type==pygame.KEYDOWN:
			if event.key==pygame.K_e:
				c.otherkey["e"]=True
			if event.key==pygame.K_m:
				game.stage="map" if game.stage=="play" else "play"
			if event.key==pygame.K_q:
				game.player.placing_bridge=True if game.player.placing_bridge==False else False

	if game.stage=="play":
		game.player.update()
		game.world.cover=make_hole(game.world.cover,make_circle_surf(15,(255,255,255)),add_poses(game.player.mappos,(-15,-15)))
		game.scroll=[game.player.pos[0]-screen_width/2+5,game.player.pos[1]-screen_height/2+7]
		game.player.draw()
		for d in game.world.derclist:
			d.draw()
		for y in range(math.floor(game.scroll[1]/16)-5,math.floor(game.scroll[1]/16)+15):
			
			for x in range(math.floor(game.scroll[0]/16)-5,math.floor(game.scroll[0]/16)+30):
				try:
					tile=game.world.tiles[y][x]
				except IndexError:
					continue
				if type(tile)==Tile:
					tile.draw()
		"""
		for tile in game.world.tilelist:
			tile.draw()
		"""
		testsin.update()
		testsin.draw((0,0))
	elif game.stage=="map":
		screen.blit(game.world.map,(0,0))
		screen.blit(game.world.cover,(0,0))
		screen.blit(make_surf((3,3),(255,0,0)),[game.player.mappos[0]-1,game.player.mappos[1]-1])

	pygame.display.set_caption(f" fps:{clock.get_fps()}")
	screen=pygame.transform.scale(screen,window.get_size())
	window.blit(screen,(0,0))
	pygame.display.update()
    
pygame.quit()
