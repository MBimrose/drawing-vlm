from build123d import *
import math

outer_radius = 25.0
inner_radius = 12.0
body_height = 60.0
flange_radius = 40.0
flange_thickness = 15.0
fillet_radius = 3.0
chamfer_distance = 1.0
hole_diameter = 5.0
hole_count = 6
hole_circle_radius = 35.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (inner_radius, body_height))
            l2 = Line(l1@1, (outer_radius, body_height))
            l3 = Line(l2@1, (outer_radius, flange_thickness))
            l4 = Line(l3@1, (flange_radius, flange_thickness))
            l5 = Line(l4@1, (flange_radius, 0))
            l6 = Line(l5@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, body_height/2) * Cylinder(hole_diameter/2, body_height + 20)

part = solid_body
part.name = "revolved_flange_with_holes"
export_step(part, "output.step")