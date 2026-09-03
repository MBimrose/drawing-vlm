from build123d import *
import math

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
hex_radius = 30.0
hole_diameter = 6.0
countersink_diameter = 12.0
countersink_angle = 82.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 3
hole_cols = 4
chamfer_size = 0.5
rib_width = 8.0
rib_length = 30.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)
base = p.part

with BuildPart() as hp:
    with BuildSketch() as hs:
        RegularPolygon(hex_radius, 6)
    extrude(amount=plate_thickness)
hex_prism = hp.part

result = base - hex_prism

rib_top = Pos(0, plate_width/2 - rib_width/2, plate_thickness/2) * Box(rib_length, rib_width, plate_thickness)
rib_bottom = Pos(0, -plate_width/2 + rib_width/2, plate_thickness/2) * Box(rib_length, rib_width, plate_thickness)
result = result + rib_top + rib_bottom

csk_radius = hole_diameter / 2
csk_sink_radius = countersink_diameter / 2
csk_height = (csk_sink_radius - csk_radius) / math.tan(math.radians(countersink_angle / 2))

for row in range(hole_rows):
    for col in range(hole_cols):
        x = (col - (hole_cols - 1) / 2) * hole_spacing_x
        y = (row - (hole_rows - 1) / 2) * hole_spacing_y
        cyl = Pos(x, y, plate_thickness/2) * Cylinder(csk_radius, plate_thickness)
        cone = Pos(x, y, plate_thickness - csk_height/2) * Cone(csk_radius, csk_sink_radius, csk_height)
        result = result - (cyl + cone)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_hex_cutout_ribs_and_holes"
export_step(part, "output.step")