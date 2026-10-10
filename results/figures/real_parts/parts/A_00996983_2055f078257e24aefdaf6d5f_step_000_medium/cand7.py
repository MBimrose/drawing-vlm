from build123d import *
import math

base_radius = 40.0
hex_radius = 30.0
lower_height = 30.0
upper_height = 60.0
rib_count = 12
rib_width = 5.0
rib_thickness = 3.0
rib_height = lower_height
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_radius)
    with BuildSketch(Plane.XY.offset(upper_height)) as s2:
        RegularPolygon(hex_radius, 6)
    loft()

solid_body = p.part

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(base_radius - rib_thickness/2, 0, rib_height/2) * Box(rib_thickness, rib_width, rib_height)
    solid_body = solid_body + rib

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = fillet(bottom_edges, fillet_radius)

part = solid_body
part.name = "lofted_hex_with_ribs"
export_step(part, "output.step")