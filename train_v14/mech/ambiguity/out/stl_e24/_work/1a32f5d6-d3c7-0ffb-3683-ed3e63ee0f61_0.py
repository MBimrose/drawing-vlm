from build123d import *
import math

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
hex_radius = 25.0
hex_depth = 4.0
hole_diameter = 6.0
countersink_diameter = 12.0
countersink_angle = 82.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
num_holes_x = 4
num_holes_y = 3
edge_chamfer = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part

with BuildPart() as hp:
    with BuildSketch(Plane.XY.offset(plate_thickness)) as hs:
        RegularPolygon(hex_radius, 6)
    extrude(amount=-hex_depth)
solid_body = solid_body - hp.part

csk_radius = countersink_diameter / 2
csk_height = csk_radius / math.tan(math.radians(countersink_angle / 2))
hole_radius = hole_diameter / 2

for i in range(num_holes_x):
    for j in range(num_holes_y):
        x = (i - (num_holes_x - 1) / 2) * hole_spacing_x
        y = (j - (num_holes_y - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, plate_thickness / 2) * Cylinder(hole_radius, plate_thickness)
        solid_body = solid_body - Pos(x, y, plate_thickness - csk_height / 2) * Cone(0, csk_radius, csk_height)

part = solid_body
part.name = "plate_with_hex_cutout_and_countersunk_holes"
export_step(part, "output.step")