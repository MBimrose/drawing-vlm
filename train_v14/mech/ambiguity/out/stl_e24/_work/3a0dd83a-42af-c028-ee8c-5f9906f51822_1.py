from build123d import *

base_radius = 12.0
shoulder_radius = 20.0
body_length = 30.0
shoulder_length = 10.0
boss_radius = 10.0
boss_height = 8.0
cavity_depth = 20.0
cavity_radius = 6.0
through_hole_diameter = 8.0
counterbore_diameter = 12.0
counterbore_depth = 3.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((base_radius, 0), (base_radius, body_length))
            l2 = ThreePointArc(l1 @ 1, (shoulder_radius, body_length + shoulder_length / 2), (shoulder_radius, body_length + shoulder_length))
            l3 = Line(l2 @ 1, (boss_radius, body_length + shoulder_length + boss_height))
            l4 = Line(l3 @ 1, (0, body_length + shoulder_length + boss_height))
            l5 = Line(l4 @ 1, (base_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

solid_body = solid_body - Pos(0, 0, body_length + shoulder_length + boss_height - counterbore_depth / 2) * Cylinder(counterbore_diameter / 2, counterbore_depth)
solid_body = solid_body - Pos(0, 0, (body_length + shoulder_length + boss_height) / 2) * Cylinder(through_hole_diameter / 2, body_length + shoulder_length + boss_height + 10)

with BuildPart() as cav:
    with BuildSketch(Plane.XZ) as csk:
        with BuildLine() as cbl:
            cl1 = Line((base_radius, 0), (cavity_radius, cavity_depth))
            cl2 = Line(cl1 @ 1, (0, cavity_depth))
            cl3 = Line(cl2 @ 1, (base_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = solid_body - cav.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "revolved_body_with_cavity"
export_step(part, "output.step")