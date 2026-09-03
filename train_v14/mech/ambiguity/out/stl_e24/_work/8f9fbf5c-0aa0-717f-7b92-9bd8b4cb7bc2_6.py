from build123d import *
import math

plate_length = 70.0
plate_width = 40.0
plate_thickness = 8.0
cutout_major = 20.0
cutout_minor = 12.0
hole_diameter = 5.0
countersink_diameter = 8.5
countersink_angle = 82.0
chamfer_size = 0.5
rib_height = 2.0
rib_width = 6.0
rib_length = 30.0
hole_offset_x = 15.0
hole_offset_y = 10.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

with BuildPart() as cutout_p:
    with BuildSketch() as cutout_s:
        Ellipse(cutout_major/2, cutout_minor/2)
    extrude(amount=plate_thickness + 0.1)
solid_body = solid_body - Pos(0, plate_width/4, 0) * cutout_p.part

shaft_r = hole_diameter / 2
csk_r = countersink_diameter / 2
csk_h = (csk_r - shaft_r) / math.tan(math.radians(countersink_angle / 2))

hole_positions = [
    (0, plate_width/2 - hole_offset_y),
    (-hole_offset_x, -plate_width/2 + hole_offset_y),
    (hole_offset_x, -plate_width/2 + hole_offset_y)
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(shaft_r, plate_thickness + 0.1)
    solid_body = solid_body - Pos(x, y, plate_thickness - csk_h/2) * Cone(shaft_r, csk_r, csk_h)

rib = Pos(0, 0, rib_height/2) * Box(rib_width, rib_length, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_cutout_holes_and_rib"
export_step(part, "output.step")