from build123d import *
import math

base_radius = 40.0
top_radius = 30.0
base_height = 25.0
top_height = 35.0
rib_count = 12
rib_width = 5.0
rib_height = 8.0
chamfer_angle = 30.0
chamfer_distance = base_radius * math.tan(math.radians(chamfer_angle)) * 0.1
hole_diameter = 10.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_radius)
    extrude(amount=base_height)
    with BuildSketch(Plane.XY.offset(base_height)) as s2:
        RegularPolygon(top_radius, 6)
    extrude(amount=top_height)

solid_body = p.part
solid_body = solid_body - Cylinder(hole_diameter/2, base_height + top_height + 10)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(base_radius - rib_width/2, 0, base_height/2) * Box(rib_width, rib_height, base_height)
    solid_body = solid_body + rib

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

part = solid_body
part.name = "ribbed_hexagonal_body"
export_step(part, "output.step")