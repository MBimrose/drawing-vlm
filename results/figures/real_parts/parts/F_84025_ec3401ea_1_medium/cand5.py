from build123d import *
import math

body_diameter = 50.0
body_height = 60.0
flange_diameter = 80.0
flange_thickness = 15.0
wall_thickness = 5.0
pocket_width = 30.0
pocket_length = 40.0
pocket_depth = 8.0
hole_diameter = 7.0
hole_count = 6
hole_radius = (flange_diameter/2) - wall_thickness - hole_diameter/2
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (flange_diameter/2, 0))
            l2 = Line(l1@1, (flange_diameter/2, flange_thickness))
            l3 = Line(l2@1, (body_diameter/2, flange_thickness))
            l4 = Line(l3@1, (body_diameter/2, body_height))
            l5 = Line(l4@1, (0, body_height))
            l6 = Line(l5@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = offset(solid_body, amount=-wall_thickness, openings=solid_body.faces())

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

pocket = Pos(0, 0, body_height - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)
solid_body = solid_body - pocket

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_radius * math.cos(angle)
    py = hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, body_height/2) * Cylinder(hole_diameter/2, body_height + 20)

part = solid_body
part.name = "revolved_flanged_body"
export_step(part, "output.step")