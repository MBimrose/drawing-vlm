from build123d import *

total_length = 70.0
outer_diameter = 40.0
inner_diameter = 20.0
step1_length = 10.0
step2_length = 12.0
step1_diameter = 30.0
step2_diameter = outer_diameter
keyway_width = 5.0
keyway_depth = 8.0
chamfer_distance = 2.0
set_screw_diameter = 4.0
set_screw_position = total_length / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (outer_diameter/2, 0), (outer_diameter/2, step1_length),
                     (step1_diameter/2, step1_length), (step1_diameter/2, step1_length + step2_length),
                     (step2_diameter/2, step1_length + step2_length), (step2_diameter/2, total_length),
                     (0, total_length), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, total_length/2) * Cylinder(inner_diameter/2, total_length)
solid_body = solid_body - Pos(inner_diameter/2, 0, total_length/2) * Box(keyway_width, keyway_depth, total_length)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)
solid_body = solid_body - Pos(0, 0, set_screw_position) * Rot(0, 90, 0) * Cylinder(set_screw_diameter/2, outer_diameter)

part = solid_body
part.name = "stepped_shaft_with_keyway"
export_step(part, "output.step")