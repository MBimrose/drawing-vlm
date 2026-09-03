from build123d import *
import math

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
hex_radius = 20.0
hex_height = 4.0
hole_diameter = 6.0
countersink_diameter = 12.0
countersink_angle = 82.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 4
chamfer_size = 1.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 4.0

base = Box(plate_length, plate_width, plate_thickness)

with BuildPart() as hp:
    with BuildSketch() as hs:
        RegularPolygon(hex_radius, 6)
    extrude(amount=hex_height)
hex_boss = hp.part

result = base + hex_boss

pocket = Pos(0, 0, plate_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

csk_half_angle = math.radians(countersink_angle / 2)
csk_height = (countersink_diameter/2 - hole_diameter/2) / math.tan(csk_half_angle)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        hole = Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)
        csk = Pos(x, y, plate_thickness/2 - csk_height/2) * Cone(hole_diameter/2, countersink_diameter/2, csk_height)
        result = result - hole - csk

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

part = result
part.name = "plate_with_hex_boss"
export_step(part, "output.step")