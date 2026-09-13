import turtle
screen=turtle.Screen()
screen.title("unforutnatley we ran out of budgte for the real ms paint so i made this garbge instead")
screen.bgcolor("white")
turtle=turtle.Turtle()
turtle.color("black")
turtle.speed(0)
turtle.hideturtle()
turtle.penup()
def imnotafurry(event):turtle.pendown()
def ilied_iAmAFurry(event):turtle.penup()
def meow_nyah(event):
    #i hate how 0,0 is in th emiddel instead of top left cuz its so weird and my brain hurts
    x=event.x-screen.window_width()/2
    y=screen.window_height()/2-event.y
    #hashtag turtle is so annoying why did you pick this thing anyway
    turtle.goto(x,y)
there_once_was_aShipAtSeaandthenameof_theShip_wasabillyoftea=screen.getcanvas()
there_once_was_aShipAtSeaandthenameof_theShip_wasabillyoftea.bind('<Button-1>',imnotafurry)
there_once_was_aShipAtSeaandthenameof_theShip_wasabillyoftea.bind('<ButtonRelease-1>',ilied_iAmAFurry)
there_once_was_aShipAtSeaandthenameof_theShip_wasabillyoftea.bind('<Motion>',meow_nyah)
screen.mainloop()