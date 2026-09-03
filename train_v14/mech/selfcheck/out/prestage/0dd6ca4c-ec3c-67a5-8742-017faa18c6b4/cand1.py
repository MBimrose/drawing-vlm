from build123d import *

base_radius = 15.0
base_height = 15.0
shoulder_radius = 25.0
shoulder_height = 35.0
top_radius = 10.0
total_height = 80.0
hole_diameter = 10.0
hole_depth = total_height - 5.0
countersink_diameter = 16.0
countersink_angle = 82.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (base_radius, 0), (base_radius, base_height),
                     (shoulder_radius, base_height + shoulder_height),
                     (top_radius, total_height), (0, total_height), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, 0) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, hole_depth, countersink_angle)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "revolved_profile_with_hole"
export_step(part, "output.step")