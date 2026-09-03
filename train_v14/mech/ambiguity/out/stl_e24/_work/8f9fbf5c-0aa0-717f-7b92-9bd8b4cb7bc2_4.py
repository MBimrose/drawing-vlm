from build123d import *
import math

plate_width = 70.0
plate_height = 40.0
plate_thickness = 8.0
oval_width = 25.0
oval_height = 12.0
oval_depth = 4.0
oval_offset_y = 10.0
hole_diameter = 5.0
csk_diameter = 8.5
csk_angle = 82
hole_offset = 12.0
rib_width = 6.0
rib_height = 4.0
rib_thickness = 2.0
rib_offset_y = -plate_height/2 + 10.0
chamfer_size = 0.5

solid_body = Box(plate_width, plate_height, plate_thickness)

with BuildPart() as oval_p:
    with BuildSketch(Plane.XY.offset(plate_thickness/2)) as oval_sk:
        Ellipse(oval_width/2, oval_height/2)
    extrude(amount=-oval_depth)
solid_body = solid_body - Pos(0, oval_offset_y, 0) * oval_p.part

csk_radius = csk_diameter / 2
csk_height = csk_radius / math.tan(math.radians(csk_angle / 2))
hole_radius = hole_diameter / 2

hole_positions = [
    (-plate_width/2 + hole_offset, -plate_height/2 + hole_offset),
    (plate_width/2 - hole_offset, -plate_height/2 + hole_offset),
    (0, plate_height/2 - hole_offset)
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_radius, plate_thickness + 0.1)
    solid_body = solid_body - Pos(x, y, plate_thickness/2 - csk_height/2) * Cone(0, csk_radius, csk_height)

rib = Pos(0, rib_offset_y, -plate_thickness/2 + rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "plate_with_oval_pocket_and_holes"
export_step(part, "output.step")