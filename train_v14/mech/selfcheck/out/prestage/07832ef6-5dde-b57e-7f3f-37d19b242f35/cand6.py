from build123d import *
import math

total_height = 80.0
flange_thickness = 20.0
shaft_radius = 8.0
flange_outer_radius = 38.0
rib_width = 6.0
rib_height = 12.0
rib_count = 6
hole_diameter = 5.0
hole_depth = 12.0
hole_radius = 20.0
hole_count = 4
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (shaft_radius, 0))
            l2 = Line(l1@1, (shaft_radius, total_height - flange_thickness))
            l3 = Line(l2@1, (flange_outer_radius, total_height - flange_thickness))
            l4 = Line(l3@1, (flange_outer_radius, total_height))
            l5 = Line(l4@1, (0, total_height))
            l6 = Line(l5@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

rib = Pos(shaft_radius + rib_width/2, 0, total_height - flange_thickness/2) * Box(rib_width, rib_height, flange_thickness)
for i in range(rib_count):
    angle = i * 360.0 / rib_count
    solid_body = solid_body + Rot(0, 0, angle) * rib

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_radius * math.cos(angle)
    py = hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, total_height - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "revolved_flange_with_ribs"
export_step(part, "output.step")