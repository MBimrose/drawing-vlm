from build123d import *
import math

hex_radius = 30.0
hex_height = 60.0
rib_thickness = 5.0
rib_height = 20.0
rib_count = 12
chamfer_size = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        RegularPolygon(hex_radius, 6)
    extrude(amount=hex_height)

solid_body = p.part

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_size)

rib_radius = hex_radius + rib_thickness / 2
for i in range(rib_count):
    angle = math.radians(i * 360.0 / rib_count)
    px = rib_radius * math.cos(angle)
    py = rib_radius * math.sin(angle)
    rib = Pos(px, py, rib_height / 2) * Cylinder(rib_thickness / 2, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "hex_with_ribs"
export_step(part, "output.step")