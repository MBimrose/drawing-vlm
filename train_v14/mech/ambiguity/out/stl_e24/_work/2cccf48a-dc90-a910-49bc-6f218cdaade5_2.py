from build123d import *
import math

plate_width = 80.0
plate_height = 60.0
plate_thickness = 5.0
tab_width = 20.0
tab_height = 10.0
slot_width = 30.0
slot_height = 12.0
hole_diameter = 5.5
hole_circle_radius = 20.0
chamfer_size = 0.8

base = Box(plate_width, plate_height, plate_thickness)
tab = Pos(0, -(plate_height/2 + tab_height/2), 0) * Box(tab_width, tab_height, plate_thickness)
solid = base + tab

slot = Box(slot_width, slot_height, plate_thickness)
solid = solid - slot

hole_positions = [(0, 0)] + [
    (hole_circle_radius * math.cos(math.radians(a)),
     hole_circle_radius * math.sin(math.radians(a)))
    for a in [0, 90, 180, 270]
]
for x, y in hole_positions:
    solid = solid - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_size)

part = solid
part.name = "WallMountPlate"
export_step(part, "output.step")