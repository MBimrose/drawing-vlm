from build123d import *
import math

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
hex_radius = 30.0
hex_depth = 4.0
hole_diameter = 6.0
countersink_diameter = 12.0
countersink_angle = 82.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
num_holes_x = 4
num_holes_y = 2
notch_width = 10.0
notch_depth = 8.0
rib_height = 2.0
rib_width = 5.0

solid = Box(plate_length, plate_width, plate_thickness)

with BuildPart() as hp:
    with BuildSketch(Plane.XY.offset(plate_thickness/2)) as s:
        RegularPolygon(hex_radius, 6)
    extrude(amount=-hex_depth)
solid = solid - hp.part

csk_half_angle = math.radians(countersink_angle / 2)
csk_height = (countersink_diameter/2 - hole_diameter/2) / math.tan(csk_half_angle)
csk_cone = Pos(0, 0, -csk_height/2) * Cone(hole_diameter/2, countersink_diameter/2, csk_height)
csk_cyl = Pos(0, 0, -csk_height - 10) * Cylinder(hole_diameter/2, 20)
csk_tool = csk_cone + csk_cyl

for i in range(num_holes_x):
    for j in range(num_holes_y):
        x = (i - (num_holes_x-1)/2) * hole_spacing_x
        y = (j - (num_holes_y-1)/2) * hole_spacing_y
        solid = solid - Pos(x, y, plate_thickness/2) * csk_tool

notch = Box(notch_width, notch_depth, plate_thickness)
solid = solid - Pos(-plate_length/2 + notch_width/2, plate_width/2 - notch_depth/2, 0) * notch
solid = solid - Pos(plate_length/2 - notch_width/2, plate_width/2 - notch_depth/2, 0) * notch

rib = Pos(0, 0, rib_height/2) * Box(plate_length - 2*notch_width, rib_width, rib_height)
solid = solid + rib

part = solid
part.name = "plate_with_hex_pocket_and_holes"
export_step(part, "output.step")