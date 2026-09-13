global l := false
global r := false
setmousedelay 0

!F1::
{
    global l
    l := !l
}

!F2::
{
    global r
    r := !r
}

SetTimer(Clicker, 1)

Clicker()
{
    global l, r
    if l
        Click()
    if r
        Click("right")
}
