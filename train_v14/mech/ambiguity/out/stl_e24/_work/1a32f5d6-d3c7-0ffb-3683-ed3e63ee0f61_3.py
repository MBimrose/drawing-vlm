from build123d import *
import math

plate_width = 80.0
plate_height = 60.0
plate_thickness = 6.0
hex_radius = 25.0
chamfer_size = 0.8
hole_diameter = 6.0
csk_diameter = 12.0
csk_angle = 82.0
hole_margin = 8.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0

base = Box(plate_width, plate_height, plate_thickness)

with BuildPart() as hp:
    with BuildSketch() as hs:
        RegularPolygon(hex_radius, 6)
    extrude(amount=plate_thickness * 2)
hex_cut = hp.part

plate = base - hex_cut

csk_radius = csk_diameter / 2
csk_height = csk_radius / math.tan(math.radians(csk_angle / 2))
shaft_radius = hole_diameter / 2

points = []
for i in range(4):
    x = -plate_width/2 + hole_margin + i * hole_spacing_x
    points.append((x, plate_height/2 - hole_margin))
    points.append((x, -plate_height/2 + hole_margin))
for i in range(2):
    y = -plate_height/2 + hole_margin + i * hole_spacing_y
    points.append((-plate_width/2 + hole_margin, y))
    points.append((plate_width/2 - hole_margin, y))

for x, y in points:
    plate = plate - Pos(x, y, 0) * Cylinder(shaft_radius, plate_thickness * 2)
    plate = plate - Pos(x, y, plate_thickness/2 - csk_height/2) * Cone(0, csk_radius, csk_height)

vertical_edges = plate.edges().filter_by(Axis.Z)
plate = chamfer(vertical_edges, chamfer_size)

part = plate
part.name = "plate_with_hex_cutout_and_holes"
export_step(part, "output.step")