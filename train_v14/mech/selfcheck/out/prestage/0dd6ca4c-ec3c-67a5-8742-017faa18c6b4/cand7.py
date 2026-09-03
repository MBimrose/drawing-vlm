from build123d import *
import math

base_radius = 15.0
base_height = 15.0
shoulder_radius = 25.0
shoulder_height = 25.0
top_radius = 10.0
total_height = 80.0
bore_radius = 5.0
countersink_diameter = 12.0
countersink_angle = 82.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1@1, (base_radius, base_height))
            l3 = Line(l2@1, (shoulder_radius, base_height + shoulder_height))
            l4 = Line(l3@1, (top_radius, total_height))
            l5 = Line(l4@1, (0, total_height))
            l6 = Line(l5@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Cylinder(bore_radius, total_height + 2)

csk_depth = (countersink_diameter/2 - bore_radius) / math.tan(math.radians(countersink_angle/2))
csk_cone = Pos(0, 0, total_height - csk_depth/2) * Cone(bore_radius, countersink_diameter/2, csk_depth)
solid_body = solid_body - csk_cone

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

part = solid_body
part.name = "revolved_profile_with_bore"
export_step(part, "output.step")