from build123d import *
import math

flange_outer_radius = 30.0
flange_height = 10.0
eyelet_outer_radius = 20.0
eyelet_thickness = 15.0
eyelet_inner_radius = 8.0
lid_hole_diameter = 5.0
lid_hole_count = 6
lid_hole_radius = 25.0
chamfer_size = 1.0

total_height = flange_height + eyelet_thickness

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0,0), (flange_outer_radius, 0))
            l2 = Line(l1@1, (flange_outer_radius, flange_height))
            l3 = Line(l2@1, (eyelet_outer_radius, flange_height))
            l4 = Line(l3@1, (eyelet_outer_radius, total_height))
            l5 = Line(l4@1, (0, total_height))
            l6 = Line(l5@1, (0,0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, total_height/2) * Cylinder(eyelet_inner_radius, total_height)

for i in range(lid_hole_count):
    angle = math.radians(i * 360.0 / lid_hole_count)
    px = lid_hole_radius * math.cos(angle)
    py = lid_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, total_height/2) * Cylinder(lid_hole_diameter/2, total_height + 10)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "flange_eyelet"
export_step(part, OUTPUT_PATH)