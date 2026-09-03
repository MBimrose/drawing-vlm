from build123d import *

overall_length = 70.0
outer_diameter = 40.0
inner_diameter = 20.0
grip_section_length = 12.0
grip_section_diameter = 30.0
base_section_length = 10.0
keyway_width = 6.0
keyway_depth = 4.0
set_screw_hole_diameter = 4.0
set_screw_hole_offset = 35.0
chamfer_distance = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
grip_radius = grip_section_diameter / 2.0
grip_start = base_section_length
grip_end = base_section_length + grip_section_length

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, grip_start))
            l2 = Line(l1@1, (grip_radius, grip_start))
            l3 = Line(l2@1, (grip_radius, grip_end))
            l4 = Line(l3@1, (outer_radius, grip_end))
            l5 = Line(l4@1, (outer_radius, overall_length))
            l6 = Line(l5@1, (inner_radius, overall_length))
            l7 = Line(l6@1, (inner_radius, 0))
            l8 = Line(l7@1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

solid_body = solid_body - Pos(0, 0, overall_length/2) * Cylinder(inner_radius, overall_length)
solid_body = solid_body - Pos(inner_radius - keyway_depth/2, 0, overall_length/2) * Box(keyway_depth, keyway_width, overall_length)
solid_body = solid_body - Pos(0, 0, set_screw_hole_offset) * Rot(0, 90, 0) * Cylinder(set_screw_hole_diameter/2, outer_diameter)

part = solid_body
part.name = "handle_with_keyway"
export_step(part, "output.step")