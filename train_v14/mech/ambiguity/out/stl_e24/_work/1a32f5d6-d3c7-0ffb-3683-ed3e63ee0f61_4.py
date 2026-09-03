from build123d import *
import math

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
hex_radius = 25.0
hex_depth = 3.0
hole_diameter = 6.0
countersink_diameter = 12.0
countersink_angle = 82.0
hole_margin = 8.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
num_holes_x = 4
num_holes_y = 2

base = Box(plate_length, plate_width, plate_thickness)

with BuildPart() as hex_cut:
    with BuildSketch(Plane.XY.offset(plate_thickness)) as sk:
        RegularPolygon(hex_radius, 6)
    extrude(amount=-hex_depth)
base = base - hex_cut.part

start_x = -plate_length/2 + hole_margin
start_y = -plate_width/2 + hole_margin
points = []
for i in range(num_holes_x):
    for j in range(num_holes_y):
        x = start_x + i*hole_spacing_x
        y = start_y + j*hole_spacing_y
        points.append((x, y))

csk_radius = countersink_diameter / 2
csk_height = csk_radius / math.tan(math.radians(countersink_angle / 2))
hole_radius = hole_diameter / 2

for x, y in points:
    base = base - Pos(x, y, 0) * Cylinder(hole_radius, plate_thickness)
    base = base - Pos(x, y, plate_thickness/2 - csk_height/2) * Cone(0, csk_radius, csk_height)

part = base
part.name = "plate_with_hex_cutout_and_countersunk_holes"
export_step(part, "output.step")