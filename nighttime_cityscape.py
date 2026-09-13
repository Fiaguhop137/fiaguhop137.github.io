import random,pygame,string
WIDTH,HEIGHT=600,600
FPS=24
pygame.init()
screen=pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Nighttime Cityscape")
clock=pygame.time.Clock()
def buildings(canvas,width,height,min_height,max_height,building_color):
    x=0
    y=height
    while x<width:
        h=random.randint(min_height,max_height)
        w=random.randint(1,width//10)
        pygame.draw.rect(canvas,pygame.Color(building_color),(x,y-h,w,h))
        wincnty=random.randint(0,h//5)+1
        wincntx=random.randint(0,w//5)+1
        winwidth=w//wincntx
        winheight=h//wincnty
        for j in range(wincnty-1):
            for k in range(wincntx-1):
                pygame.draw.rect(canvas,pygame.Color("#"+(random.choice(list(string.hexdigits))+random.choice(list(string.hexdigits)))*2+"00"),(x+k*winwidth+winwidth//4,y-h+j*winheight+winheight//4,winwidth//2,winheight//2))
        if random.random()<1/5:
            pygame.draw.line(canvas,pygame.Color(building_color),(x+w//2,y-h),(x+w//2,y-h-random.randint(5,20)))
        x+=w
def make_city():
    canvas=pygame.Surface((WIDTH,HEIGHT))
    canvas.fill(pygame.Color("#050e39"))
    y=HEIGHT
    for i in range(30):
        for j in range(i*HEIGHT//30):
            x=random.randrange(WIDTH)
            pygame.draw.circle(canvas,pygame.Color("#ffffff"),(x,y),random.choice([0,0,0,0,1,2]))
            y-=1
        y=HEIGHT
    pygame.draw.circle(canvas,pygame.Color("#bbddff"),(WIDTH//6,HEIGHT//6),WIDTH//12)
    pygame.draw.circle(canvas,pygame.Color("#050e39"),(WIDTH//8+WIDTH//12,HEIGHT//8),WIDTH//16)
    min_building_heights=[HEIGHT//5,HEIGHT//4,HEIGHT//3]
    buildings(canvas,WIDTH,HEIGHT,min_building_heights[0],HEIGHT-min_building_heights[0],"#000000")
    buildings(canvas,WIDTH,HEIGHT,min_building_heights[1],HEIGHT-min_building_heights[1],"#111111")
    buildings(canvas,WIDTH,HEIGHT,min_building_heights[2],HEIGHT-min_building_heights[2],"#222222")
    return canvas
city=make_city()
running=True
while running:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_SPACE:
                city=make_city()
    screen.blit(city,(0,0))
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()