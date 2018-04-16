## Before Use it
Install these packages.
```
sudo apt install xbacklight python-gi python-gi-cairo python3-gi python3-gi-cairo gir1.2-gtk-3.0
```

Then, run this command.
```
xrandr -q | grep " connected"
# DVI-D-1 connected primary 1920x1080+0+0 (normal left inverted right x axis y axis) 476mm x 268mm

```
Next, modify "OUTPUT" value in GUI_XRandR.py to your display name. In my environment, it is "DVI-D-1".


## How to use

```
python GUI_XRandR.py
```
