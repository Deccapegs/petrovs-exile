print("init")

import pygame,asyncio

class why_pygbag():
	pls=pygame
#from modules.perlin_noise import PerlinNoise as Pnoise
async def main(p):
	import itertools
	import functools
	import math,random,threading,sys,asyncio
	from functools import reduce
	from operator import mul
	pygame=p.pls
	def dot(
	    vec1,
	    vec2,
	) -> [float, int]:
	    """Two vectors dot product.

	    Parameters:
	        vec1: List[float] - first vector
	        vec2: List[float] - second vector

	    Returns:
	        Dot product of 2 vectors

	    Raises:
	        ValueError: if length not equal
	    """
	    if len(vec1) != len(vec2):
	        raise ValueError("lengths of two vectors are not equal")
	    return sum([val1 * val2 for val1, val2 in zip(vec1, vec2)])


	def sample_vector(dimensions: int, seed: int):
	    """Sample normalized vector given length.

	    Parameters:
	        dimensions: int - space size
	        seed: Optional[int] - random seed value

	    Returns:
	        List[float] - normalized random vector of given size
	    """
	    st = random.getstate()
	    random.seed(seed)

	    vec = []
	    for _ in range(dimensions):
	        vec.append(random.uniform(-1, 1))  # noqa: S311

	    random.setstate(st)
	    return vec


	def fade(given_value: float) -> float:
	    """Smoothing [0, 1] values.

	    Parameters:
	        given_value: float [0, 1] value for smoothing

	    Returns:
	        smoothed [0, 1] value

	    Raises:
	        ValueError: if input not in [-0.1, 1.1]
	    """
	    if given_value < -0.1 or given_value > 1.1:  # noqa: WPS459, WPS432
	        raise ValueError("expected to have value in [-0.1, 1.1]")
	    return (
	        6 * math.pow(given_value, 5)  # noqa: WPS432
	        - 15 * math.pow(given_value, 4)  # noqa: WPS432, W503
	        + 10 * math.pow(given_value, 3)  # noqa: WPS432, W503
	    )


	def hasher(
	    coordinates,
	    tile_sizes = None,
	) -> int:
	    """Hashes coordinates to integer number and use obtained number as seed.

	    Parameters:
	        coordinates: Tuple[int, ...] - tuple of coordinates
	        tile_sizes: Optional[Tuple[int, ...]] - optional tile sizes

	    Returns:
	        hash of coordinates in integer
	    """
	    if tile_sizes:
	        coordinates = tuple(
	            coors % tile for coors, tile in zip(coordinates, tile_sizes)
	        )
	    # fmt: off
	    return max(
	        1,
	        int(
	            abs(
	                dot([10**coordinate for coordinate in range(len(coordinates))], coordinates) + 1,  # noqa: E501, WPS221
	            ),
	        ),
	    )
	    # fmt: on


	def product(iterable) -> float:
	    """Multiplies values of iterable  each with each.

	    Parameters:
	        iterable: - any iterable

	    Returns:
	        product of values
	    """
	    if len(iterable) == 1:
	        return iterable[0]
	    return iterable[0] * product(iterable[1:])
	class RandVec:

	    def __init__(self, coordinates, seed: int):
	        """Vector initializer in specified coordinates.

	        Parameters:
	            coordinates: Tuple[int] - vector coordinates
	            seed: int - random init seed
	        """
	        self.coordinates = coordinates
	        self.vec = sample_vector(dimensions=len(self.coordinates), seed=seed)

	    def dists_to(self, coordinates):
	        """Calculate distance to given coordinates.

	        Parameters:
	            coordinates: Tuplie[int] - coordinates to calculate distance

	        Returns:
	            distance

	        """
	        return tuple(
	            coor1 - coor2 for coor1, coor2 in zip(coordinates, self.coordinates)
	        )

	    def weight_to(self, coordinates) -> float:
	        """Calculate this vector weights to given coordinates.

	        Parameters:
	            coordinates: Tuple[int] - target coordinates

	        Returns:
	            weight
	        """
	        # fmt: off
	        weighted_dists = [fade(1 - abs(dist)) for dist in self.dists_to(coordinates)]  # noqa: E501, WPS221
	        # fmt: on
	        return reduce(mul, weighted_dists)

	    def get_weighted_val(self, coordinates) -> float:
	        """Calculate weighted contribution of this vec to final result.

	        Parameters:
	            coordinates: calculate weighted relative to this coordinates

	        Returns:
	            weighted contribution
	        """
	        return self.weight_to(coordinates) * dot(
	            self.vec,
	            self.dists_to(coordinates),
	        )

	class Pnoise:

	    def __init__(self, octaves: float = 1, seed = None):
	        """Perlin Noise object initialization class.

	            ex.: noise = PerlinNoise(n_dims=2, octaves=3.5, seed=777)

	        Parameters:
	            octaves : optional positive float, default = 1
	                positive number of sub rectangles in each [0, 1] range
	            seed : optional positive int, default = None
	                specified seed

	        Raises:
	            ValueError: if seed is negative
	        """
	        if octaves <= 0:
	            raise ValueError("octaves expected to be positive number")

	        if seed is not None and not isinstance(seed, int) and seed <= 0:
	            raise ValueError("seed expected to be positive integer number")

	        self.octaves: float = octaves
	        self.seed: int = seed if seed else random.randint(1, 10**5)  # noqa: S311, E501
	        self.cache: Dict[Tuple, RandVec] = {}

	    def __call__(
	        self,
	        coordinates,
	        tile_sizes = None,
	    ) -> float:
	        """Forward request to noise function.

	        Parameters:
	            coordinates: float or list of coordinates
	            tile_sizes: optional tile sizes to repetative patterns

	        Returns:
	            noise_value
	        """
	        return self.noise(coordinates, tile_sizes)

	    def noise(  # noqa: WPS231
	        self,
	        coordinates,
	        tile_sizes = None,
	    ) -> float:
	        """Get perlin noise value for given coordinates.

	        Parameters:
	            coordinates: float or list of coordinates
	            tile_sizes: optional tile sizes to repetative patterns

	        Returns:
	            noise_value

	        Raises:
	            TypeError: if coordinates is not valid type
	            ValueError: if tile_sizes have different length than coordinates
	        """
	        if not isinstance(coordinates, (int, float, list, tuple)):
	            raise TypeError("coordinates must be int, float or iterable")

	        if isinstance(coordinates, (int, float)):
	            coordinates = [coordinates]
	        else:
	            coordinates = list(coordinates)

	        if tile_sizes is not None:
	            if isinstance(tile_sizes, int):
	                tile_sizes = [tile_sizes]
	            # fmt: off
	            if not all(isinstance(tile, int) for tile in tile_sizes):
	                raise TypeError("tile_sizes must be int or list of int")
	            # fmt: on

	            if len(tile_sizes) != len(coordinates):
	                raise ValueError("tile_sizes must have same length as coordinates")

	            coordinates = [coors % tile for coors, tile in zip(coordinates, tile_sizes)]
	            tile_sizes = tuple(tile * self.octaves for tile in tile_sizes)
	        coordinates = [coordinate * self.octaves for coordinate in coordinates]

	        coor_bounding_box = [
	            (math.floor(coordinate), math.floor(coordinate) + 1)
	            for coordinate in coordinates
	        ]
	        return sum(
	            [
	                self.get_from_cache_of_create_new(coors, tile_sizes).get_weighted_val(
	                    coordinates,
	                )
	                for coors in itertools.product(*coor_bounding_box)
	            ]  # noqa: C812
	        )
	    @functools.lru_cache(maxsize=100, typed=False)  # noqa: B019
	    def get_from_cache_of_create_new(
	        self,
	        coors,
	        tile_sizes = None,
	    ) -> RandVec:
	        """Use cached RandVec or creates new.

	        Parameters:
	            coors: Tuple of int vector coordinates
	            tile_sizes: optional tile sizes to repetative patterns

	        Returns:
	            RandVec
	        """
	        return RandVec(coors, self.seed * hasher(coors, tile_sizes))

	pygame.init()
	pygame.mixer.pre_init(44100,-16,2,512)
	pygame.mixer.init()
	screen_width=342
	screen_height=174
	info=pygame.display.Info()
	window= pygame.display.set_mode((info.current_w,info.current_h-63),pygame.RESIZABLE)
	screen=pygame.Surface((screen_width,screen_height)).convert()
	pygame.display.set_caption("waves")
	clock=pygame.time.Clock()
	class Para():
		def __init__(self,text_:list,height=7):
			self.text=text_
			if text_==[]:
				self.para=pygame.Surface((1,1),pygame.SRCALPHA).convert_alpha()
			else:
				self.para=pygame.Surface((max(len(line) for line in text_)*height,len(text_)*height),pygame.SRCALPHA).convert_alpha()
			self.para.fill((0,0,0,0))
			for y in range(len(text_)):
					self.para.blit(text.render(str(self.text[y])),(0,y*height))
			self.img=self.para
	def get_noise(noise,size=[10,10]):
		return [[noise([x/size[0],y/size[1]]) for x in range(size[0])] for y in range(size[1])]
	def add_poses(p1,p2):
		return (p1[0]+p2[0],p1[1]+p2[1])
	def get_dist(p1,p2):
		return ((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)**0.5
	def withoutscroll(pos):
		return [pos[0]+game.scroll[0],pos[1]+game.scroll[1]]
	def withscroll(pos,mult=1):
		return [(pos[0]-game.scroll[0]*mult),(pos[1]-game.scroll[1]*mult)]
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
	def remove_list(list_,rlist):

		for item in rlist:
			try:
				list_.remove(item)
			except ValueError:
				pass
		return list_
	def ran_sign():
		return 1 if random.random()>0.5 else -1
	def collide_bullet(self,bullets):
		indexs=self.rect.collidelistall(bullets)
		for i in indexs:
			if self.rect.clipline(*bullets[i].line):
				bullets[i].pop()
				return i
		return -1
	class Sin():
		def __init__(self,frequency,height,start=0):
			self.frequency=frequency
			self.height=height
			self.val=0
			self.start=start
			self.timer=start
			self.reset_=1/frequency*math.pi*2
		def update(self):
			self.timer+=self.frequency
			self.timer%=self.reset_
			self.val=math.sin(self.timer)*self.height
		def reset(self):
			self.timer=self.start

	class types():
		def __init__(self):
			self.grass=1
			self.rock_tile=2
			self.air=0

			self.purple=0
			self.yellow=1
			self.red=2
			self.blue=3

			self.tree=0
			self.rock=1
			self.bush=3
			self.chest=4
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
			"e":[False,False]
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
				self.otherkey[k][1]=self.otherkey[k][0]

				self.otherkey[k][0]=key[getattr(pygame,f"K_{k}")]
	c=c()
	def get_surf_from_sheet(sheet,sheetpos,size):
		s=pygame.Surface(size,pygame.SRCALPHA).convert_alpha()
		s.fill((0,0,0,0))
		s.blit(sheet,sheetpos)
		return s
	sfx={
		"jump":[pygame.mixer.Sound(f"sfx/jump_{i}.wav") for i in range(1,5)],
		"shoot":[pygame.mixer.Sound(f"sfx/shoot_{i}.wav") for i in range(1,4)],
		"p_hit":[pygame.mixer.Sound(f"sfx/hit_{i}.wav") for i in range(1,4)],
		"get_gem":[pygame.mixer.Sound("sfx/get_gem.wav")],
		"build":[pygame.mixer.Sound(f"sfx/build_{i}.wav") for i in range(1,3)],
		"dig":[pygame.mixer.Sound(f"sfx/dig_{i}.wav") for i in range(1,3)],
		"talk":[pygame.mixer.Sound("sfx/talk.wav")],
		"e_die":[pygame.mixer.Sound(f"sfx/enemy_die_{i}.wav") for i in range(1,4)],
		"wind":[pygame.mixer.Sound("sfx/wind.wav")]


	}
	for key in sfx:
		for sound in sfx[key]:
			sound.set_volume(0.3)
	pygame.mixer.music.load("sfx/ambiance.wav")
	pygame.mixer.music.play(-1)
	pygame.mixer.music.set_volume(0)
	sfx["wind"][0].set_volume(0)
	imgs={
		"tilesheet":pygame.image.load("imgs/tiles.png").convert_alpha(),
		"text":pygame.image.load("imgs/text.png").convert_alpha(),
		"player":pygame.image.load("imgs/petrov.png").convert_alpha(),
		"foliage_sheet":pygame.image.load("imgs/foliage.png").convert_alpha(),
		"items":pygame.image.load("imgs/items.png").convert_alpha(),
		"gem_sheet":pygame.image.load("imgs/gems.png").convert_alpha(),
		"enemy_sheet":pygame.image.load("imgs/enemies.png").convert_alpha(),
		"diabox":pygame.image.load("imgs/diabox.png").convert_alpha(),
		"rbox":pygame.image.load("imgs/rbox.png").convert_alpha(),
		"e_to_interact":pygame.image.load("imgs/e to interact.png").convert_alpha(),
		"npcs":pygame.image.load("imgs/npcs.png").convert_alpha(),
		"death":pygame.image.load("imgs/death.png").convert(),
		"win":pygame.image.load("imgs/win.png").convert()
	}
	imgs.update({
		"wood_bridge":get_surf_from_sheet(imgs["tilesheet"],(0,-96),(16,16)),
		"shovel":get_surf_from_sheet(imgs["tilesheet"],(-16,-96),(16,16)),
		"small_rock":get_surf_from_sheet(imgs["foliage_sheet"],(0,-13),(14,8)),
		"rock_derc":get_surf_from_sheet(imgs["foliage_sheet"],(0,0),(22,13)),
		"rock_sheet":get_surf_from_sheet(imgs["tilesheet"],(-48,0),(48,96)),
		"small_tree":get_surf_from_sheet(imgs["foliage_sheet"],(-22,0),(11,12)),
		"tree":get_surf_from_sheet(imgs["foliage_sheet"],(0,-21),(51,43)),
		"small_tree_2":get_surf_from_sheet(imgs["foliage_sheet"],(-58,0),(13,12)),
		"wood":get_surf_from_sheet(imgs["items"],(0,0),(15,13)),
		"rock":get_surf_from_sheet(imgs["items"],(0,-13),(10,10)),
		"gems":{
		t.purple:get_surf_from_sheet(imgs["gem_sheet"],(0,0),(16,23)),
		t.yellow:get_surf_from_sheet(imgs["gem_sheet"],(-16,0),(16,32)),
		t.red:get_surf_from_sheet(imgs["gem_sheet"],(-32,0),(16,23)),
		t.blue:get_surf_from_sheet(imgs["gem_sheet"],(-48,0),(16,32)),
		},
		"small_rock_sheet":get_surf_from_sheet(imgs["tilesheet"],(-36,-112),(24,48)),
		"small_grass_sheet":get_surf_from_sheet(imgs["tilesheet"],(0,-112),(36,72)),
		"enemy_stump":get_surf_from_sheet(imgs["enemy_sheet"],(0,0),(16,16)),
		"enemy_orb":get_surf_from_sheet(imgs["enemy_sheet"],(-16,0),(16,16)),
		"enemy_stalactite":get_surf_from_sheet(imgs["enemy_sheet"],(-32,0),(16,16)),
		"coin":get_surf_from_sheet(imgs["items"],(-15,0),(13,13)),
		"cartographer":get_surf_from_sheet(imgs["npcs"],(0,0),(24,19)),
		"merchant":get_surf_from_sheet(imgs["npcs"],(-26,0),(7,16)),
		"bush":get_surf_from_sheet(imgs["foliage_sheet"],(-71,0),(16,12)),
		"chest":get_surf_from_sheet(imgs["foliage_sheet"],(-37,0),(16,12)),
		"berry":get_surf_from_sheet(imgs["items"],(-10,-13),(13,11)),
		"tut":get_surf_from_sheet(imgs["items"],(-73,0),(7,17))


		})
	s=pygame.Surface((16,16),pygame.SRCALPHA).convert_alpha()
	s.blit(imgs["berry"],(0,0))
	pygame.display.set_icon(s)
	del s
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
				self.img.blit(self.frames,(0,0))
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
	class sinfx():
		def __init__(self,height,frequency,length,delay,colour,thickness=2,angle=0,cached_wave=None):
			self.height=height
			self.frequency=frequency
			self.length=length
			self.speed=delay
			self.colour=colour
			self.angle=angle
			size=(length,height*2)
			self.size=size
			if  cached_wave!=None:
				self.imgs=cached_wave.imgs
				self.img=animation(self.imgs,self.imgs[0].get_size(),delay)

				return None
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
			self.img.draw(pos)
	class ripplefx():
		def __init__(self,interval,thickness,speed,radius,colour=(255,0,255),cached_ripple=None):
			self.interval=interval
			self.thickness=thickness
			self.speed=speed
			self.radius=radius
			self.colour=colour
			self.rings=[]
			for i in range(self.radius):
				surf=pygame.Surface((self.radius*2,self.radius*2),pygame.SRCALPHA).convert_alpha()
				pygame.draw.circle(surf,self.colour,(self.radius,self.radius),i,width=self.thickness)
				self.rings.append(surf)
			self.timer=0
		def update(self):
			self.timer+=self.speed
			self.timer%=self.interval
		def draw(self,pos=(0,0)):
			for i in range(self.radius):
				if math.floor((i+self.timer))%self.interval==0:
					screen.blit(self.rings[i],pos)
	class ripple():
		def __init__(self,ripple,pos,recoil=5,parent=None):
			self.ripple=ripple
			self.radius=ripple.radius
			self.recoil=recoil
			self.pos=pos
			self.parent=parent
		def update(self):
			self.ripple.update()
			if get_dist(game.player.rect.center,add_poses(self.pos,(self.radius,self.radius)))<=self.radius:
				game.player.damage()
			if self.parent!=None:
				self.pos=add_poses(self.parent.rect.center,(-self.radius,-self.radius))
		def update_parent(self,parent):
			self.parent=parent
		def draw(self):
			self.ripple.draw(withscroll(self.pos))




	class bgsin():
		def __init__(self,height,frequency,length,speed,colour,thickness,pos=[0,0],smoothness=5,fade=True,slope=0):
			self.height=height
			self.frequency=frequency
			self.length=length
			self.speed=speed
			self.colour=colour
			self.timer=0
			self.thickness=thickness
			self.smoothness=smoothness
			self.pos=pos
			self.fade=fade
			self.slope=slope
			self.renew_points()
		def renew_points(self):
			self.points=[]
			for x in range(math.ceil(self.length)):
				self.points.append((x+self.pos[0],(math.sin((x+self.timer)*self.frequency)*self.height
					+abs(x-self.length/2)*self.slope
					)*(-2*abs(x-self.length/2)/self.length+1 if self.fade else 1)+self.pos[1]
					))
		def update(self,**kwargs):
			self.timer+=self.speed
			for key,val in kwargs.items():
				setattr(self,key,(getattr(self,key)*(self.smoothness-1)+val)/self.smoothness)
			self.renew_points()
		def renew_attr(self,**kwargs):
			for key,val in kwargs.items():
				setattr(self,key,(getattr(self,key)*(self.smoothness-1)+val)/self.smoothness)
		def draw(self):
			pygame.draw.lines(screen, self.colour, False, self.points, self.thickness)

	class Particle:
			def __init__(self
					,size:float or int
					,pos:list
					,angle=0
					,totalspeed=0
					,colour=(255,255,255)
					,gravity=0
					,xgravity=0
					,lifeloss=0.1
					,staticspeed=[0,0]
					,alphaloss=0
					,alpha=255
					,flag=pygame.BLENDMODE_NONE
					,delay=0
					,friction=0.95
					):
				self.pos=list(pos)
				self.angle=math.radians(angle)
				self.size=size
				self.totalspeed=totalspeed
				self.staticspeed=list(staticspeed)
				self.colour=colour
				self.alpha=alpha
				self.flag=flag
				self.gravity=gravity
				self.xgravity=xgravity
				self.lifeloss=lifeloss
				self.alphaloss=alphaloss
				self.img=pygame.Surface((size*2,size*2),pygame.SRCALPHA)
				self.delay=delay
				self.delaytimer=0
				self.friction=friction
				game.particles.append(self)
			def update(self):
				if self.delaytimer>self.delay:
					self.staticspeed[0]*=self.friction
					self.staticspeed[1]*=self.friction
					self.totalspeed*=self.friction
					self.staticspeed[1]+=self.gravity
					self.staticspeed[0]+=self.xgravity
					self.pos[0]+=math.sin(self.angle)*self.totalspeed
					self.pos[1]+=math.cos(self.angle)*self.totalspeed
					self.pos[0]+=self.staticspeed[0]
					self.pos[1]+=self.staticspeed[1]
					self.img=pygame.Surface((self.size*2,self.size*2),pygame.SRCALPHA)
					self.img.fill((0,0,0,0))
					pygame.draw.circle(self.img,self.colour,(self.size,self.size),self.size)
					self.alpha-=self.alphaloss
					self.img.set_alpha(self.alpha)
					self.size-=self.lifeloss
					if self.size<=0 or self.alpha<=0:
						game.remove_particles.append(self)
						del self
						return None
				else:
					self.delaytimer+=1
			def draw(self):
				screen.blit(self.img,withscroll((self.pos[0]-self.size,self.pos[1]-self.size)),special_flags=self.flag)


	cached_player_bullets={i*22.5:sinfx(5.5,0.3,32,3 ,(60,200,220),angle=i*22.5) for i in range(-16,16)}
	cached_purple_bullets={i*22.5:sinfx(5.5,1,32,3 ,(225,55,170),angle=i*22.5) for i in range(-16,16)}



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
		def __init__(self,img,pos,anchor="bottomleft",health=3,items={},lists=[],mappos=[0,0],type_=None):
			self.pos=list(pos)
			self.img=img
			self.health=health
			self.items=items
			self.mappos=mappos
			self.type=type_
			try:
				self.rect=self.img.get_rect()
				self.size=self.img.get_size()
			except AttributeError:
				self.size=self.img.img.get_size()
				self.rect=self.img.img.get_rect()
			setattr(self.rect,anchor,self.pos)
			for list_ in lists:
				list_.append(self)
			
		def update(self):
			try:
				self.img.update()
			except AttributeError:
				pass
			for bullet in game.player_bullets:	
				if self.rect.clipline(*bullet.line):
					colour=(255,255,0)
					if self.type==t.tree:
						colour=(198,89,58)
					elif self.type==t.rock:
						colour=(84,84,69)
					elif self.type==t.bush:
						colour=(47,116,120)
					elif self.type==t.chest:
						colour=(160,85,70)

					for i in range(5):
						Particle(3*random.random()+2,bullet.rect.center,angle=math.degrees(bullet.angle)+90+random.random()*30-15,colour=colour,totalspeed=random.random()*2+2,gravity=0,lifeloss=0.1)
					bullet.pop()
					self.health-=1

					if self.health<=0:
						random.choice(sfx["e_die"]).play()
						for key,item in self.items.items():
							game.player.add_inventory(key,item)
							Notice(f"+{item} {key}",imgs[key])
							Particle(3,self.rect.center,lifeloss=-0.2,alphaloss=5,colour=colour)

						try:
							game.world.derclist.remove(self)
							game.world.decrs[self.mappos[1]][self.mappos[0]]=None
							del self
						except ValueError:
							pass
						return
		def draw(self):

			try:
				screen.blit(self.img,withscroll((self.rect.topleft)))
			except TypeError:
				self.img.draw(withscroll((self.rect.topleft))) 
	class Tile():
		def __init__(self,img,pos,sheetpos=(0,0),lists=[],scroll_mult=1,size=16):
			self.img=get_surf_from_sheet(img,sheetpos,(size,size))
			self.pos=pos
			self.rect=self.img.get_rect(topleft=self.pos)
			self.active=True
			self.scroll_mult=scroll_mult
			for list_ in lists:
				list_.append(self)
			self.mappos=[self.pos[0]/16,self.pos[1]/16]
		def update(self):
			if self.active==False:
				self.img.set_alpha(64)
			else:
				self.img.set_alpha(255)
		def draw(self):
			#screen.blit(self.img,withscroll(self.pos))
			screen.blit(self.img,withscroll(self.pos,self.scroll_mult))
	class Gem():
		def __init__(self,img,pos,type_=t.purple,lists=[],gem_surf=None):
			self.img=img
			self.pos=list(pos)
			self.type=type_
			self.rect=img.get_rect(topleft=self.pos)
			self.gem_surf=gem_surf
			self.sin=Sin(1/60,6)
			for list_ in lists:
				list_.append(self)
			self.lists=lists
		def update(self):
			self.sin.update()
			if game.player.rect.colliderect(self.rect):
				Notice("one step closer to freedom...")
				game.player.increase_gem_count()
				random.choice(sfx["get_gem"]).play()
				Particle(1,self.rect.center,lifeloss=-0.4,alphaloss=3,colour=(255,255,255))
				self.pop()
				return
		def pop(self):
			for list_ in self.lists:
				try:
					list_.remove(self)
				except ValueError:
					pass
			del self
			return

		def draw(self):
			screen.blit(self.img,withscroll((self.pos[0],self.pos[1]+math.floor(self.sin.val))))
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
			def check_side_val(pos,val,sides=[None,None,None,None]):
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
			def Auto_tile(x,y,data):
				sheetpos=[0,0]
				if data[y][x]==t.air:
					return(0,0)
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
				return sheetpos
			self.bignoise=Pnoise(octaves=12,seed=round(random.random()*10000000))
			print("c")
			self.noise=Pnoise(octaves=35,seed=round(random.random()*10000000))
			self.finenoise=Pnoise(octaves=100,seed=round(random.random()*10000000))
			self.finemult=Pnoise(octaves=35,seed=round(random.random()*10000000))
			self.rock_noise=Pnoise(octaves=12,seed=round(random.random()*10000000))
			self.tree_noise=Pnoise(octaves=12,seed=round(random.random()*10000000))
			self.parallax=Pnoise(octaves=32,seed=round(random.random()*10000000))
			self.parallax_back=Pnoise(octaves=50,seed=round(random.random()*10000000))
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
			tree_array=get_noise(self.tree_noise,self.size)
			parallax_array=get_noise(self.parallax,[math.ceil(self.size[0]*2/3),math.ceil(self.size[1]*2/3)])
			self.data=[[0 for x in range(self.size[0])] for y in range(self.size[1])]
			self.tiles=[[None for x in range(self.size[0])] for y in range(self.size[1])]
			self.derclist=[]
			self.tilelist=[]
			#self.parallaxdata=list(self.data)
			#self.parallaxtiles=list(self.tiles)
			self.parallaxlist=[]
			self.decrs=[[None for x in range(self.size[0])] for y in range(self.size[1])]
			self.gemlist=[]
			self.gem_surfs=[]
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
			
					#if -0.28>height:
					#	self.parallaxdata[y][x]=t.grass
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
					sheetpos=Auto_tile(x,y,data)
					
				
					if val==t.grass:
						self.tiles[y][x]=Tile(imgs["tilesheet"],[x*16,y*16],sheetpos=sheetpos,lists=[self.tilelist])	
					if val==t.rock_tile:
						self.tiles[y][x]=Tile(imgs["rock_sheet"],[x*16,y*16],sheetpos=sheetpos,lists=[self.tilelist])	
			#place structs
			rock_palletee=((103,98,85),(84,89,69),(119,101,86),(70,85,57))
			tree_pallette=((45,175,132),(50,193,128),(63,204,120),(32,153,130))
			rock_init_poses=[[math.floor(random.random()*self.size[0]),math.floor(random.random()*self.size[1])] for _ in range(200)]
			tree_init_poses=[[math.floor(random.random()*self.size[0]),math.floor(random.random()*self.size[1])] for _ in range(1000)]
			bush_init_poses=[[math.floor(random.random()*self.size[0]),math.floor(random.random()*self.size[1])] for _ in range(50)]
			chest_init_poses=[[math.floor(random.random()*self.size[0]),math.floor(random.random()*self.size[1])] for _ in range(20)]
			def check_air(xy):
				if xy[1]+1>self.size[1] or xy[1]-1<0:
					return True
				else:
					try:
						return self.data[xy[1]+1][xy[0]]==0
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

							pos=[math.floor(random.random()*self.size[0]),math.floor(random.random()*self.size[1])]
					if random.random()<=0.5:

						self.decrs[pos[1]][pos[0]]=decr(imgs["small_rock"],[pos[0]*16+2,pos[1]*16+10],anchor="topleft",lists=[self.derclist],items={"rock":2},mappos=pos,type_=t.rock)
					else:
						self.decrs[pos[1]][pos[0]]=decr(imgs["rock_derc"],[pos[0]*16-3,pos[1]*16+5],anchor="topleft",lists=[self.derclist],items={"rock":4},mappos=pos,type_=t.rock)

			num=0
			yotal=0
			for pos in tree_init_poses:
				if 0<tree_array[pos[1]][pos[0]]<0.2:
					continue
				else:
					tree_type=0
					if random.random()<0.6:
						tree_type=0
					else:
						if random.random()>0.2:
							tree_type=1
						else:
							tree_type=2
					for _ in range(1000):
						if check_air(pos):
							pos[1]+=1
						elif self.data[pos[1]][pos[0]]:
							pos[1]-=1
						
						if pos[1]>self.size[1] or pos[1]<0:
							pos=[math.floor(random.random()*self.size[0]),math.floor(random.random()*self.size[1])]
						try:
							if self.data[pos[1]+1][pos[0]]==t.rock_tile:
								pos=[math.floor(random.random()*self.size[0]),math.floor(random.random()*self.size[1])]
							if tree_type==2:
								count=0
								for i in range(-1,2):
									if data[pos[1]+1][pos[0]-i]==t.grass:
										count+=1
								
								if count==3:
									num+=1
									break
								else:
									pos=[math.floor(random.random()*self.size[0]),math.floor(random.random()*self.size[1])]

						except IndexError:
							pass

						
					if tree_type==0:
						self.decrs[pos[1]][pos[0]]=decr(imgs["small_tree"],[pos[0]*16+3,pos[1]*16+6],anchor="topleft",lists=[self.derclist],items={"wood":2},mappos=pos,type_=t.tree)
					elif tree_type==1:
						self.decrs[pos[1]][pos[0]]=decr(imgs["small_tree_2"],[pos[0]*16+3,pos[1]*16+6],anchor="topleft",lists=[self.derclist],items={"wood":3},mappos=pos,type_=t.tree)
					elif tree_type==2:
						yotal+=1
						self.decrs[pos[1]][pos[0]]=decr(imgs["tree"],[pos[0]*16-24,pos[1]*16-24],anchor="topleft",lists=[self.derclist],health=10,items={"wood":5},mappos=pos,type_=t.tree)
			for pos in chest_init_poses:
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

							pos=[math.floor(random.random()*self.size[0]),math.floor(random.random()*self.size[1])]

					self.decrs[pos[1]][pos[0]]=decr(imgs["chest"],[pos[0]*16+2,pos[1]*16+5],anchor="topleft",lists=[self.derclist],items={"coin":random.randint(1,2)*random.randint(1,2)*random.randint(1,2),random.choice(("rock","berry","wood")):random.randint(1,2)},mappos=pos,type_=t.chest)
			for pos in bush_init_poses:
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

							pos=[math.floor(random.random()*self.size[0]),math.floor(random.random()*self.size[1])]
						try:
							if self.data[pos[1]+1][pos[0]]==t.rock_tile:
								pos=[math.floor(random.random()*self.size[0]),math.floor(random.random()*self.size[1])]
						except IndexError:
							pass
					self.decrs[pos[1]][pos[0]]=decr(imgs["bush"],[pos[0]*16+2,pos[1]*16+5],anchor="topleft",lists=[self.derclist],items={"berry":2},mappos=pos,type_=t.bush)


			gem_points=[]
			count=0
			while len(gem_points)<4:
				num=len(gem_points)
				add=[0,0]
				if num==1:
					add[0]=self.size[0]/2*16

				elif num==2:
					add[1]=self.size[1]/2*16
				elif num==3:
					add=[self.size[0]/2*16,self.size[1]/2*16]
				point=[math.floor(random.random()*16*self.size[0]/2+add[0]),math.floor(random.random()*16*self.size[1]/2+add[1])]
				
				for other_point in gem_points:
					if get_dist(point,other_point)<64*16:
						break
				else:
					if get_dist(point,[self.size[0]/2,self.size[1]/2])<64*16:
						pass
					else:
						gem_points.append(point)
				if count>4000:
					gem_points.append(point)

					break
				count+=1


			for i,point in enumerate(gem_points):
				#point=[self.size[0]/2*16,self.size[1]/2*16]
				mappos=[point[0]/16,point[1]/16]
				colour=(255,0,255)
				if i ==t.purple:
					colour=(185,35,255)
				elif i==t.yellow:
					colour=(255,255,0)
				elif i==t.red:
					colour=(221,55,39)
				elif i==t.blue:
					colour=(0,255,255)
				surf=[mappos[0]-1,mappos[1]-1],make_surf((3,3),colour)
				gem=Gem(imgs["gems"][i],point,lists=[self.gemlist],gem_surf=surf)
				self.gem_surfs.append(surf)


				"""
				for _ in range(1000):
					if check_air(pos):
						pos[1]+=1
					elif self.tiles[pos[1]][pos[0]]
				"""
	class Bullet():
		def __init__(self,pos,speed,angle,wave,parent=None,damage=1,explode=False):
			self.pos=list(pos)
			self.speed=int(speed)
			self.angle=math.radians(angle)
			self.wave=wave
			self.rect=wave.img.img.get_rect(center=self.pos)
			self.pop_timer=0
			self.damage=damage
			game.bullets.append(self)
			if parent==game.player:
				game.player_bullets.append(self)
			self.parent=parent
			self.line=[[0,0],[0,0]]
		def update(self):
			
			self.pos[0]+=math.cos(self.angle)*self.speed
			self.pos[1]+=-math.sin(self.angle)*self.speed
			self.rect.center=self.pos
			self.wave.update()
			self.pop_timer+=1
			if self.pop_timer>360:
				self.pop()
				return
			tiles=self.rect.collidelistall(game.collide_tiles)
			const=10
			line=[
			[math.cos(self.angle)*const+self.pos[0],-math.sin(self.angle)*const+self.pos[1]],
			[math.cos(-self.angle-math.pi)*const+self.pos[0],-math.sin(self.angle-math.pi)*const+self.pos[1]]]
			self.line=line
			#pygame.draw.line(screen,(255,0,255),withscroll(line[0]),withscroll(line[1]))
			for tile in tiles:
				tile=game.loaded_tiles[tile]
				if tile.rect.clipline(*line):

					self.pop(bypass=False)
					return
		def draw(self):

			#pygame.draw.rect(screen,(255,0,255),self.rect)
			self.wave.draw(withscroll(self.rect.topleft))
		def pop(self,bypass=True):
			if self.pop_timer>5 or bypass:
				game.remove_bullets.append(self)
				if self.parent==game.player:
					try:
						game.player_bullets.remove(self)
					except ValueError:
						pass
				
				del self
				return
	class Expolsion():
		def __init__(self,pos,radius,recoil=6,ripple=None):
			self.ripple=ripple
			self.radius=radius
			self.pos=pos
			self.recoil=recoil
			self.active=True
			game.expolsions.append(self)
		def update(self):
			"update ripple vfx"
			if not self.active:
				return
			if get_dist(self.pos,game.player.rect.center)<=self.radius:
				angle=math.atan2(-(self.pos[1]-game.player.rect.center[1]),self.pos[0]-game.player.rect.center[0])-math.pi/4
				game.player.rocket_jump(self.recoil,angle)
				print(f"angle: {math.degrees(angle)}")

			
			self.active=False
		def draw(self):
			pass
		def pop(self):
			game.remove_expolsions.append(self)
	def get_wave_angle(angle):
		return math.floor(angle/22.5+0.5)*22.5%360
	def get_mouse_player_angle():
		point=-(mouse_get_pos()[1]-screen_height/2+5),mouse_get_pos()[0]-screen_width/2+7
		angle=math.degrees(math.atan2(*point))
		return angle
	class bhellring():
		def __init__(self,bullets,pos,waves=cached_player_bullets,speed=1,interval=30,angle=0,angle_change=1,parent=None,type_juice=False,start_time=0):
			self.bullets=bullets
			self.angle=angle
			self.parent=parent
			self.angle_change=angle_change
			self.interval=interval
			self.pos=pos
			self.timer=start_time
			self.speed=speed
			self.waves=waves
			
		def update(self):
			self.timer+=1
			self.angle+=self.angle_change
			try:
				self.pos=self.parent.rect.center
			except AttributeError:
				pass
			if self.timer>=self.interval:
				for i in range(self.bullets):
					angle=self.angle+(i*360)/self.bullets
					Bullet(list(self.pos),self.speed,angle,wave=self.waves[get_wave_angle(angle)])
				self.timer=0
		def update_parent(self,parent):
			self.parent=parent
	class bhellpattern():
		def __init__(self,angle,pos,waves=cached_purple_bullets,angle_change=1,angle_wave_hertz=0,angle_wave_height=0,spray=0,interval=90,speed=3,telegraph=False,followplayer=False,parent=None,type_juice=False,start_time=0):
			self.angle=angle
			self.pos=pos
			self.angle_change=angle_change
			self.spray=spray
			self.angle_sin_f=angle_wave_hertz
			self.angle_wave_height=angle_wave_height
			self.sintimer=0
			self.sinoffset=0
			self.interval=interval
			self.timer=start_time
			self.speed=speed
			self.telegraph=telegraph
			self.followplayer=followplayer
			self.parent=parent
			self.waves=waves
			
		def update(self):
			self.timer+=1
			self.sintimer+=self.angle_sin_f
			if self.timer>=self.interval:
				if self.parent!=None:
					self.pos=self.parent.rect.center
				self.angle+=self.angle_change
				self.sinoffset=math.sin(self.sintimer)*self.angle_wave_height
				angle=(math.degrees(math.atan2(-(game.player.pos[1]-self.pos[1]),game.player.pos[0]-self.pos[0])) if self.followplayer==True else self.angle)+self.sinoffset+random.random()*self.spray
				Bullet(list(self.pos),self.speed,angle,self.waves[get_wave_angle(angle)])
				self.timer=0

		def update_parent(self,parent):
			self.parent=parent
	class Enemy():
		def __init__(self,pos,img,pattens,health=3,gravity=0,speed=0,grounded=False,roofed=False,items={"coin":2}):
			for patten in pattens:
				patten.update_parent(self)
			self.img=img
			self.pos=[math.floor(pos[0]),math.floor(pos[1])]
			self.grav=int(gravity)
			self.speed=int(speed)
			self.health=int(health)
			self.pattens=pattens
			self.rect=self.img.get_rect(topleft=self.pos)
			self.items=items
			game.enemies.append(self)
			coled=False
			if self.rect.collidelist(game.loaded_tiles)!=-1:
				for _ in range(170):
					self.pos[1]-=1
					self.rect.y=self.pos[1]
					if self.rect.collidelist(game.loaded_tiles)==-1:
						coled=True
						break
				if not coled:
					self.pop()
			coled=False
			if roofed:
				for _ in range(170):
					self.pos[1]-=1
					self.rect.y=self.pos[1]
					if self.rect.collidelist(game.loaded_tiles)!=-1:
						coled=True
						break
				if not coled:
					self.pop()
			elif grounded:
				for _ in range(170):
					self.pos[1]+=1
					self.rect.y=self.pos[1]
					if self.rect.collidelist(game.loaded_tiles)!=-1:
						coled=True
						break
				if not coled:
					self.pop()
		def update(self):
			for pattern in self.pattens:
				pattern.update()
			if collide_bullet(self,game.player_bullets)!=-1:
				self.health-=1
				Particle(1,self.rect.center,lifeloss=-0.4,alphaloss=5,colour=(89,219,46))
				if self.health<=0:
					for key,val in self.items.items():
						game.player.add_inventory(key,val)
						Notice(f"+{val} {key}",imgs[key])
					for i in range(10):
						Particle(3,self.rect.center,angle=random.random()*360,colour=(89,219,46),gravity=0,totalspeed=random.random()*1+0.1,alphaloss=4,lifeloss=-0.05,friction=1.005)
					self.pop()
					return
			if game.daynight.night[0]==False:
				self.pop()
				return

		def draw(self):
			screen.blit(self.img,withscroll(self.pos))
		def draw2(self):
			for p in self.pattens:
				try:
					p.draw()
				except AttributeError:
					continue
		def pop(self):
			game.shake([1,1],5)
			random.choice(sfx["e_die"]).play()
			game.remove_enemies.append(self)
			del self
			return


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
			self.hovering_tile=False
			self.health=10
			self.max_health=15
			self.iframes=0
			self.max_iframes=90
			self.hunger=60*180
			self.max_hunger=60*180
			self.health_bar=pygame.Rect((0,screen_height-8),(self.health/self.max_health*40,5))
			self.hunger_bar=pygame.Rect((0,screen_height-9),(self.hunger/self.max_hunger*45,1))


			self.placing_bridge=False
			self.bridge_pos=[0,0]

			self.gun_timer=0
			self.gun_interval=20
			self.recoil=2
			self.vol=0
			self.gem_count=0
			self.inventory={
			"wood":0,
			"rock":0,
			"coin":30,
			"berry":5,
			"map":0
			}

			self.rect=self.img.img.get_rect()
			self.ground_line=(self.rect.bottomleft,self.rect.bottomright)
			self.bottom_tile=game.world.tiles[math.floor(self.pos[1]/16)][math.floor(self.pos[0]/16)]
			#self.rect=pygame.Rect(self.pos,50,50)
		def update(self):
			self.iframes+=1
			self.health_bar=pygame.Rect((0,screen_height-8),(self.health/self.max_health*40,5))
			self.hunger_bar=pygame.Rect((0,screen_height-9),(self.hunger/self.max_hunger*45,1))
			self.mappos=[math.floor(self.pos[0]/16),math.floor(self.pos[1]/16)]
			for i in range(2):
				if not(-12*16<self.pos[i]<game.world.size[i]*16+12*16):
					self.pos=[game.world.size[0]*16/2,game.world.size[1]*16/2]
					Notice("you somehow wake up where you started")
					Notice("-1 health")
					self.damage()
			if c.key["s"]:
				self.speed[1]+=self.accel
			if c.key["d"]:
				self.speed[0]+=self.accel if self.grounded else self.accel/5
			if (c.key["w"] or c.key["SPACE"]) and (self.grounded or self.coyote<self.max_coyote) and (not self.jumped):
				self.speed[1]-=self.jump_power
				self.jumped=True
				random.choice(sfx["jump"]).play()
				for _ in range(5):
					Particle(4+random.random()*4,self.rect.center,angle=random.random()*360,totalspeed=0.4,lifeloss=-0.04,alphaloss=5,colour=(x:=random.random()*20+150,x,x),gravity=0.02,staticspeed=[0,-1])
			if c.key["a"]:
				self.speed[0]-=self.accel if self.grounded else self.accel/5
			self.moving=True if True in (c.key["a"],c.key["d"]) else False
			self.speed[1]+=self.grav
			if self.grounded:
				self.speed[0]*=self.fric
				self.coyote=0
			else:
				self.speed[0]*=self.airrest
				self.coyote+=1
			self.bridge_pos=(math.floor((mouse_get_pos()[0]+game.scroll[0])/16)*16,math.floor((mouse_get_pos()[1]+game.scroll[1])/16)*16)

			if self.placing_bridge:
				tile="no"
				try:
					tile=game.world.tiles[int(self.bridge_pos[1]/16)][int(self.bridge_pos[0]/16)]
				except IndexError:
					pass
				self.hovering_tile=False if tile==None else True
				if tile=="no":
					pass
				elif c.mouse[0]==[False,True]:
					
					if tile==None:
						if self.inventory["wood"]>=2 and self.inventory["rock"]>=1:
							self.inventory["wood"]-=2
							self.inventory["rock"]-=1
							random.choice(sfx["build"]).play()
							game.world.tiles[int(self.bridge_pos[1]/16)][int(self.bridge_pos[0]/16)]=Tile(imgs["wood_bridge"],self.bridge_pos,lists=[game.world.tilelist])
						else:
							Notice("2 wood and 1 rock required")
					else:
						random.choice(sfx["dig"]).play()
						tile.active=False if tile.active==True else True
			self.speed[1]*=1 if (c.key["w"] or c.key["SPACE"]) and self.speed[1]<=0 else self.airrest*0.92
			collidelist=game.collide_tiles
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
			
			indexs=self.rect.collidelistall(game.bullets)
			for i in indexs:
				if game.bullets[i] in game.player_bullets:
					continue
				if self.rect.clipline(*game.bullets[i].line):
					self.damage(game.bullets[i].damage)
					game.bullets[i].pop()

			if self.jumped:
				self.disimg=self.jump_img
			elif self.moving:
				self.img.update()
				self.disimg=self.img.img
			else:
				self.img.jumpto(0)
				self.disimg=self.idle

			self.rect.topleft=self.pos
			self.update_gun()
			self.vol=(max(0,(self.speed[0]**2+self.speed[1]**2)**0.5/12)+self.vol*14)/15
			sfx["wind"][0].set_volume(self.vol)
			if self.health<=0:
				game.stage="death"
		def update_gun(self):
			if self.placing_bridge or game.in_dialogue:
				self.gun_timer=self.gun_interval-1
				return
			if c.mouse[0][0]==True:
				if self.gun_timer>=self.gun_interval:
					random.choice(sfx["shoot"]).play()
					self.gun_timer=0
					angle=get_mouse_player_angle()
					Bullet(game.player.pos,2.5,angle,sinfx(7,1,32,1,(255,0,255),cached_wave=game.cached_player_bullets[get_wave_angle(angle)]),explode=False,parent=self)
					self.speed[0]-=math.cos(math.radians(angle))*self.recoil
					self.speed[1]+=math.sin(math.radians(angle))*self.recoil
					game.hit_bg.renew_attr(height=200)
			self.gun_timer+=1

		#	else:
		#		self.gun_timer=self.gun_interval-1
		def damage(self,amount=1):
			if self.iframes>=self.max_iframes:
				self.health-=amount
				self.iframes=0
				random.choice(sfx["p_hit"]).play()
				game.shake([1,1],10)
		def rocket_jump(self,recoil,angle):
			print(math.cos(angle)*recoil,math.sin(angle)*recoil)
			self.speed[0]-=math.cos(angle)*recoil
			self.speed[1]+=math.sin(angle)*recoil
		def add_inventory(self,item,amount):
			self.inventory[item]+=amount
		def increase_gem_count(self):
			self.gem_count+=1
		def draw(self):
			if self.placing_bridge and not self.hovering_tile:
				screen.blit(imgs["wood_bridge"],withscroll(self.bridge_pos))
			elif self.placing_bridge:
				screen.blit(imgs["shovel"],withscroll(self.bridge_pos))
			screen.blit(self.disimg,withscroll((self.pos[0]-1,self.pos[1])))
		def draw_bar(self):

			pygame.draw.rect(screen,(128,255,0),self.hunger_bar)
			pygame.draw.rect(screen,(255,0,0),self.health_bar)
	class Notice():
			def __init__(self,textv:str,image=None,begin=True):
				game.notice_board.notices.append(self)
				self.strtext=textv
				self.img=image
				if self.img==None:
					self.img=pygame.Surface((0,0))
				self.textsurf=text.render(self.strtext)
				self.noticesurf=pygame.Surface((self.textsurf.get_width()+self.img.get_width()+5,max(self.textsurf.get_height(),self.img.get_height()) ),pygame.SRCALPHA).convert_alpha()
				self.noticesurf.fill((0,0,0,0))
				self.noticesurf.blit(self.textsurf,(0,self.noticesurf.get_height()/2-self.textsurf.get_height()/2))
				self.noticesurf.blit(self.img,(self.textsurf.get_width()+1,0))
				self.fade=pygame.Surface(self.noticesurf.get_size(),pygame.SRCALPHA).convert_alpha()
				self.fade.fill((0,0,0,255/180))
				self.begindel=begin
				self.place=0
				self.timer=0
			def update(self):
				qwfx=-1
				for itemv in game.notice_board.notices:
					qwfx+=1
					if itemv==self:
						break
				self.place=qwfx
				if self.begindel==True:
					
					self.timer+=1
					if self.timer>=180:
						self.noticesurf.blit(self.fade,(0,0),special_flags=pygame.BLEND_RGBA_SUB)
						if self.timer>=360:
							game.notice_board.notices.remove(self)
							del self
			def start_pop(self):
				self.begindel=True
			def draw(self):
				screen.blit(self.noticesurf,(0,(self.place)*12+1))
	class Notification_Center():
		def __init__(self):
			self.notices=[]
			self.amount=len(self.notices)
		def update(self):
			self.amount=len(self.notices)
			for notice in self.notices:
				notice.update()
		def draw(self):
			for notice in self.notices:
				notice.draw()
	class Daynight():
		def __init__(self):
			self.timer=60*80
			self.reset=320*60
			self.night=[False,False]
			self.img=make_surf([screen_width,screen_height],(60,60,40))
		def update(self):
			self.night[1]=self.night[0]
			self.timer+=1
			self.timer%=self.reset

			if self.timer>=self.reset*2/3:
				self.night[0]=True
			else:
				self.night[0]=False
			if self.night[0]==True:
				if self.timer%(25*60)==0:
					for _ in range(2):
						Enemy(add_poses(game.player.pos,(ran_sign()*random.random()*100,ran_sign()*random.random()*100)),imgs["enemy_stalactite"],
							[bhellpattern(-90,[0,0],angle_change=0,speed=2,start_time=random.random()*90,waves=game.cached_purple_bullets,interval=90)],
							items={"coin":1,"rock":1},
							roofed=True
							)

						Enemy(add_poses(game.player.pos,(ran_sign()*random.random()*100,ran_sign()*random.random()*100)),imgs["enemy_orb"],
							[bhellring(4,[0,0],interval=120,angle_change=0.3,angle=random.random()*360,start_time=random.random()*120,waves=game.cached_purple_bullets)]
							)
						
						Enemy(add_poses(game.player.pos,(ran_sign()*random.random()*100,ran_sign()*random.random()*100)),imgs["enemy_stump"],
							[ripple(ripplefx(7,2,-0.3,24,colour=(236,194,70)),[0,0])],
							items={"coin":1,"wood":1},
							grounded=True
							)
					
		def draw(self):
			screen.blit(self.img,(0,0),special_flags=pygame.BLEND_RGB_SUB) if self.night[0] else None
	class Npc():
		def __init__(self,pos,img,speech,range_=32):
			self.img=img
			self.pos=pos
			self.tree=speech
			self.rect=self.img.get_rect(topleft=self.pos)
			self.range=range_
			self.speech=list(self.tree.keys())[0]
			self.e_to_interact=imgs["e_to_interact"]
			
			for _ in range(640):
				self.pos[1]+=1
				self.rect.y=self.pos[1]
				if self.rect.collidelist(game.world.tilelist)!=-1:
					break
			for _ in range(640):
				self.pos[1]-=1
				self.rect.y=self.pos[1]
				if self.rect.collidelist(game.world.tilelist)==-1:
					break
			self.mappos=[math.floor(self.pos[0]/16),math.floor(self.pos[1]/16)]
			game.npcs.append(self)
		def update(self):
			if c.otherkey["e"]==[True,False] and get_dist(game.player.rect.center,self.rect.center)<=self.range:
				game.speech.update_speech(*self.tree[list(self.tree.keys())[0]])
				random.choice(sfx["talk"]).play()
				game.last_npc=self
			elif get_dist(game.player.rect.center,self.rect.center)>=self.range and game.last_npc==self:
				game.in_dialogue=False

			if (not game.diamessage in [None,"exit"]) and game.last_npc==self:

				self.speech=str(game.diamessage)
		def draw(self):
			screen.blit(self.img,withscroll(self.pos))
			if get_dist(game.player.rect.center,self.rect.center)<=self.range and game.allow_e:
				screen.blit(self.e_to_interact,withscroll(add_poses(self.pos,(-2,-8))))

				

	class Speech():
		def __init__(self):
			self.box=imgs["diabox"]
			self.rbox=pygame.Surface((1,1),pygame.SRCALPHA).convert_alpha()
			self.rboxsheet=imgs["rbox"]
			self.rsize=[0,0]
			self.rtext=[text.render("unloaded 303")]
			self.speech=text.render("unloaded 404")
			self.mpressed=[False,False]
			self.hover_surf={"surf":pygame.Surface((1,1),pygame.SRCALPHA).convert_alpha(),"pos":[0,0]}
		def update_speech(self,speech_:str,responses:dict):
			self.speech=text.render(speech_)
			"""
			responses={
				"trade name 1":[items_give:dict,items_recive:dict]
				"trade name 2":[items_give:dict,items_recive:dict]
				"response 1":[None,None]
				...
			}
			"""
			game.in_dialogue=True
			self.speech=text.render(speech_) if type(speech_)==str else Para(speech_).img

			self.rtext=[[text.render(r),pygame.Rect( (0,0),(len(r)*6+2,5)),responses[r]] for i,r in enumerate(responses)]
			self.rsize=[max(r[0].get_width() for r in self.rtext)+8,len(self.rtext)*8+8]
			for i,thing in enumerate(self.rtext):
				thing[1].topleft=(4,i*8+2+screen_height-self.rsize[1]-self.box.get_height()-1)
			self.rbox=pygame.Surface(self.rsize,pygame.SRCALPHA).convert_alpha()
			for y in range(0,math.ceil(self.rsize[1])+8,8):
				for x in range(0,math.ceil(self.rsize[0])+8,8):
					if [x,y]==[0,0]:
						s=get_surf_from_sheet(self.rboxsheet,(0,0),(8,8))
					elif [x,y]==[self.rsize[0]-8,self.rsize[1]-8]:
						s=get_surf_from_sheet(self.rboxsheet,(-16,-16),(8,8))
					elif [x,y]==[0,self.rsize[1]-8]:
						s=get_surf_from_sheet(self.rboxsheet,(0,-16),(8,8))
					elif [x,y]==[self.rsize[0]-8,0]:
						s=get_surf_from_sheet(self.rboxsheet,(-16,0),(8,8))
					elif x==0:
						s=get_surf_from_sheet(self.rboxsheet,(0,-8),(8,8))
					elif y==0:
						s=get_surf_from_sheet(self.rboxsheet,(-8,0),(8,8))
					elif x==self.rsize[0]-8:
						s=get_surf_from_sheet(self.rboxsheet,(-16,-8),(8,8))
					elif y==self.rsize[1]-8:
						s=get_surf_from_sheet(self.rboxsheet,(-8,-16),(8,8))
					else:
						s=get_surf_from_sheet(self.rboxsheet,(-8,-8),(8,8))
					self.rbox.blit(s,(x,y))
		def update(self):
			self.hover_surf={"surf":pygame.Surface((1,1),pygame.SRCALPHA).convert_alpha(),"pos":[0,0]}
			m=(mouse_get_pos(),pygame.mouse.get_pressed())
			self.mpressed[1]=self.mpressed[0]
			self.mpressed[0]=m[1][0]
			for r in self.rtext:
				if r[1].collidepoint(m[0]):
					self.hover_surf={"surf":make_surf(r[1].size,(64,64,64,64),pygame.SRCALPHA),"pos":r[1].topleft}
					if self.mpressed==[True,False]:
						for take in r[2][1]:
							if r[2][1][take]>game.player.inventory[take]:
								Notice("insufficient resources")
								return None
						
						for take in r[2][1]:
							game.player.inventory[take]-=r[2][1][take]
						for give in r[2][0]:
							game.player.inventory[give]+=r[2][0][give]
							if give=="map":
								Notice("new gem location appears on your map")
							else:
								Notice(f"{give} +{r[2][0][give]}")
						if "exit" in str(r[2][2]):
							game.in_dialogue=False
						return r[2][2]




		def draw(self):
			"what spagitti and old code?"
			screen.blit(self.box,(0,145))
			screen.blit(self.speech,(4,149))
			screen.blit(self.rbox,(0,(screen_height-self.rsize[1])-self.box.get_height()-2))
			screen.blit(self.hover_surf["surf"],self.hover_surf["pos"])
			for i in range(len(self.rtext)):
				#pygame.draw.rect(screen,(255,0,255),self.rtext[i][1])
				screen.blit(self.rtext[i][0],self.rtext[i][1])
	def load_tiles(tiles,up=-5,down=15,left=-5,right=30):
		list_=[]
		for y in range(math.floor(game.scroll[1]/16)-up,math.floor(game.scroll[1]/16)+down):
			for x in range(math.floor(game.scroll[0]/16)-left,math.floor(game.scroll[0]/16)+right):
				try:
					tile=tiles[y][x]
				except IndexError:
					continue

				if type(tile)==Tile:
					list_.append(tile)
		return list_
	def load_game():
		global game
		print("a")
		l.loaded=False
		game=Game()
		game.initother()
		l.loaded=True
	class l():
		loaded=False
#	l=L()
	class Game():
		def __init__(self):
			
			global screen
			screen=pygame.Surface((screen_width,screen_height)).convert()
			screen.fill((0,0,0))
			screen.blit(text.render("loading..."),(1,1))
			screen.blit(text.render("do not worry if it says 'not responding'"),(1,8))
			screen.blit(text.render("web version will take a long time"),(1,15))
			screen=pygame.transform.scale(screen,window.get_size())
			window.blit(screen,(0,0))
			pygame.display.update()
			self.bullets=[]
			self.remove_bullets=[]
			self.player_bullets=[]
			self.expolsions=[]
			self.remove_expolsions=[]
			self.particles=[]
			self.remove_particles=[]
			self.cached_player_bullets=cached_player_bullets
			self.cached_purple_bullets=cached_purple_bullets
			self.loaded_tiles=[]
			self.loaded_dercs=[]
			self.loaded_parallax=[]
			self.collide_tiles=[]
			self.bhellpatterns=[]
			self.enemies=[]
			self.remove_enemies=[]
			self.npcs=[]
			self.allow_e=False
			self.ripples=[]
			self.stage="play"
			self.diamessage=None
			self.damage_taken=False
			self.last_npc=None
			self.notice_board=Notification_Center()
			self.daynight=Daynight()
			self.screen_shake=[0,0]
			self.shake_timer=0
			self.hit_bg=bgsin(100,0.3,int(screen_width),0.5,(90,128,230),2,pos=[0,screen_height/2],smoothness=20)
			self.bg=bgsin(50,0.15,int(screen_width),0.2,(30,90,230),5,fade=False,slope=-0.5,pos=[0,screen_height/2])
		def initother(self):
			self.world=World()
			print("b")
			self.player=Player()
			self.scroll=[self.player.pos[0]-screen_width/2+5,self.player.pos[1]-screen_height/2+7]
			self.loaded_tiles=load_tiles(self.world.tiles,down=50)
			self.speech=Speech()
			self.tut_timer=0

			self.cartographer=Npc(list(game.player.pos),imgs["cartographer"],
				{
				"sell":[["i can sell you maps to",
				"assist you on your search"],{
					"buy 1 map for 30 coin   ":[{"map":1},{"coin":30},"sell"],
					"bye  ":[{},{},"exit"]
					}]
				})
			self.merchant=Npc(list(add_poses(game.player.pos,[-16*16,0])),imgs["merchant"],
				{
				"sell":[["greetings...human, care to trade?"],{
					"buy 2 coin for 10 wood  ":[{"coin":2},{"wood":10},"sell"],
					"buy 2 coin for 5 rock ":[{"coin":2},{"rock":5},"sell"],
					"buy 2 berry for 6 coin  ":[{"berry":2},{"coin":6},"sell"],
					"just passing by":[{},{},"exit"]
					}]
				})
			self.player.pos=[self.cartographer.pos[0],self.cartographer.pos[1]]

			self.introspeech_tree={
			"d1":[
				"welcome to the isle of abyss,petrov",
				{"continue":[{},{},"d2"]}],
			"d2":[[
			"as a reminder,you are",
			"here to collect the 4 gems",
			
			],
			{"continue":[{},{},"d3"]}
			],
			"d3":[
			["if you succeed,your",
			"freedom is granted"
			],
			{"exit":[{},{},"exit_start_tut"]}
			]
			}
			self.speech.update_speech("welcome to the isle of abyss,petrov",{"continue":[{},{},"d2"]})
		def reinit(self):
			l.loaded=False
			self.__init__()
			self.initother()
			l.loaded=True
		def shake(self,amount:list,time):
			self.screen_shake=list(amount)
			self.shake_timer=time
	testsin=sinfx(5.5,0.3,32,3 ,(60,200,220),angle=45)
	testrip=ripplefx(10,2,-0.5,70)
	print("d")
	screen=pygame.Surface((screen_width,screen_height)).convert()
	screen.fill((0,0,0))
	screen.blit(text.render("loading..."),(1,1))
	screen.blit(text.render("do not worry if it says 'not responding'"),(1,8))
	screen.blit(text.render("web version will take a long time"),(1,15))
	screen=pygame.transform.scale(screen,window.get_size())
	window.blit(screen,(0,0))
	pygame.display.update()
	threading.Thread(target=load_game).start()
	test_bg=bgsin(100,0.3,int(screen_width),0.5,(50,70,210),3,pos=[0,screen_height/2],smoothness=120)
	sfx["wind"][0].play(-1)
	run= True
	while run==True:
		if not l.loaded:

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					run = False	
					pygame.quit()
					sys.exit()
			await asyncio.sleep(0)
			clock.tick(60)
			continue
		clock.tick(60)
		screen=pygame.Surface((screen_width,screen_height)).convert()
		screen.fill((40,100,230))
		c.update()
		if game.diamessage=="exit_start_tut":
			game.allow_e=True
		if game.allow_e==False:
			c.otherkey["e"]=[False,False]

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			if event.type==pygame.KEYDOWN:
				
				if event.key==pygame.K_m:
					game.stage="map" if game.stage!="map" else "play"
				elif event.key==pygame.K_n:
					game.stage="inventory" if game.stage!="inventory" else "play"
				elif event.key==pygame.K_q:
					game.player.placing_bridge=True if game.player.placing_bridge==False else False
				elif event.key==pygame.K_r:
					if game.player.inventory["berry"]>=1:
						org=int(game.player.health)
						game.player.health+=1
						game.player.health=min(game.player.max_health,game.player.health)
						Notice(f"+{game.player.health-org} health")
						Notice("-1 berry",imgs["berry"])
						game.player.add_inventory("berry",-1)
					else:
						Notice("you need berries to eat",image=imgs["berry"])
				elif event.key==pygame.K_p and (game.stage=="death" or game.stage=="win"):
					threading.Thread(target=game.reinit).start()
					while not l.loaded:
						clock.tick(60)
						for event in pygame.event.get():
							if event.type == pygame.QUIT:
								run = False
								pygame.quit()
								sys.exit()
						await asyncio.sleep(0)
						continue
				elif event.key==pygame.K_TAB:
					for n in game.notice_board.notices:
						n.start_pop()


		if game.stage=="play":
			pygame.mixer.music.set_volume(0.3)
			if game.player.gem_count>=4:
				game.stage="win"
			if game.diamessage in ["d2","d3"]:
				game.speech.update_speech(*game.introspeech_tree[game.diamessage])
				game.diamessage=None
			if game.diamessage=="exit_start_tut":
				Notice("open up your map with [m] and go to the purple point",begin=False,image=imgs["tut"])
				Notice("[tab] to dismiss",begin=False)	
				game.tut_timer+=1
				game.diamessage=None
			if 60*60>=game.tut_timer>=1:
				game.tut_timer+=1
				if game.tut_timer==60*30:
					Notice("[left click] to shoot resources",begin=False,image=imgs["tut"])
					Notice("shooting can boost you across gaps",begin=False,image=imgs["tut"])
				elif game.tut_timer==60*50:
					Notice("[q] to switch to build/ dig mode",begin=False,image=imgs["tut"])
				elif game.tut_timer==60*60:
					Notice("[n] to check your inventory",begin=False,image=imgs["tut"])
					Notice("[tab] to dismiss",begin=False)

			if game.damage_taken=="bam":
				pass
				#mirco optimisation very nessary
			elif game.damage_taken==True:
				Notice("[r] to heal",begin=False,image=imgs["tut"])
				Notice("[tab] to dismiss",begin=False)
				game.damage_taken="bam"
			elif game.damage_taken==False:
				if game.player.health!=10:
					game.damage_taken=True


			test_bg.update(height=abs(game.player.speed[0])*15+30,speed=abs(game.player.speed[1]))
			game.hit_bg.update(height=20)
			game.bg.update()
			game.daynight.update()
			game.player.update()
			game.notice_board.update()
			game.world.cover=make_hole(game.world.cover,make_circle_surf(15,(255,255,255)),add_poses(game.player.mappos,(-15,-15)))
			game.shake_timer-=1
			shake=[random.random()*game.screen_shake[0]*2-game.screen_shake[0],random.random()*game.screen_shake[1]*2-game.screen_shake[1]] if game.shake_timer>=0 else [0,0]
			game.scroll=[game.player.pos[0]-screen_width/2+5+shake[0],game.player.pos[1]-screen_height/2+7+shake[1]]
			for expolsion in game.expolsions:
				expolsion.update()

			for gem in game.world.gemlist:
				gem.update()
			for e in game.enemies:
				e.update()
			for n in game.npcs:
				n.update()
			
			
			game.loaded_tiles=[]
			game.loaded_dercs=[]
			game.collide_tiles=[]

		
			
			for y in range(math.floor(game.scroll[1]/16)-5,math.floor(game.scroll[1]/16)+15):
				for x in range(math.floor(game.scroll[0]/16)-5,math.floor(game.scroll[0]/16)+30):
					try:
						tile=game.world.tiles[y][x]
					except IndexError:
						continue

					if type(tile)==Tile:
						game.loaded_tiles.append(tile)
						if tile.active:
							game.collide_tiles.append(tile)
			for y in range(math.floor(game.scroll[1]/16)-5,math.floor(game.scroll[1]/16)+15):
				for x in range(math.floor(game.scroll[0]/16)-5,math.floor(game.scroll[0]/16)+30):
					try:
						derc_=game.world.decrs[y][x]
					except IndexError:
						continue

					if type(derc_)==decr:
						game.loaded_dercs.append(derc_)
			for tile in game.loaded_tiles:
				tile.update()
			for d in game.loaded_dercs:
				d.update()
			
		#	for tile in game.world.parallaxlist:
		#		tile.draw()
			game.bg.draw()
			test_bg.draw()
			game.hit_bg.draw()

			for d in game.loaded_dercs:
				d.draw()
			for e in game.enemies:
				e.draw()
			for tile in game.loaded_tiles:
				tile.draw()
			for n in game.npcs:
				n.draw()
			game.player.draw()
			for gem in game.world.gemlist:
				gem.draw()
			"""
			for tile in game.world.tilelist:
				tile.draw()
			"""
			#testsin.update()
			#testsin.draw((0,0))
			#testrip.update()
			#testrip.draw((0,0))
			for p in game.particles:
				p.update()
				p.draw()
			for e in game.enemies:
				e.draw2()
			for bullet in game.bullets:
				bullet.update()
				bullet.draw()

			for bullet in game.remove_bullets:
				try:
					game.bullets.remove(bullet)
				except ValueError:
					pass
			game.expolsions=remove_list(game.expolsions,game.remove_expolsions)
			game.enemies=remove_list(game.enemies,game.remove_enemies)
			game.particles=remove_list(game.particles,game.remove_particles)
			game.remove_expolsions=[]
			game.remove_bullets=[]
			game.remove_enemies=[]
			for p in game.particles:
				p.update()
			game.daynight.draw()
			game.player.draw_bar()
			game.diamessage=None
			if game.in_dialogue:
				game.diamessage=game.speech.update()
				game.speech.draw()
			game.notice_board.draw()
		elif game.stage=="map":
			screen.blit(game.world.map,(0,0))
			screen.blit(game.world.cover,(0,0))
			count=0
			for pos,surf in game.world.gem_surfs:
				if count>=game.player.inventory["map"]:
					break
				count+=1
				screen.blit(surf,pos)
			screen.blit(make_surf((3,3),(255,0,0)),[game.player.mappos[0]-1,game.player.mappos[1]-1])
			screen.blit(make_surf((3,3),(150,50,150)),game.cartographer.mappos)

		elif game.stage=="inventory":
			screen.fill((239,207,124))
			count=0
			for key,val in game.player.inventory.items():
				if key=="map":
					continue
				text_=text.render(f"{key}: {val}")
				screen.blit(text_,(6,count*16+6))
				screen.blit(imgs[key],(text_.get_size()[0]+8,count*16+6))
				count+=1
		elif game.stage=="death":
			pygame.mixer.music.set_volume(0)
			screen.blit(imgs["death"],(0,0))
		elif game.stage=="win":
			pygame.mixer.music.set_volume(0)
			screen.blit(imgs["win"],(0,0))

		pygame.display.set_caption(f"health:{game.player.health} fps:{clock.get_fps()}")
		screen=pygame.transform.scale(screen,window.get_size())
		window.blit(screen,(0,0))
		pygame.display.update()
		await asyncio.sleep(0)

	pygame.quit()
	sys.exit()
asyncio.run(main(why_pygbag))
