from build123d import *

arm_length = 80.0
outer_radius = 12.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
hole_diameter = 10.0
slot_width = 4.0
slot_depth = wall_thickness + 1.0
knurl_diameter = 2.0
knurl_depth = 2.0
knurl_spacing = 6.0
knurl_start_offset = 12.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, arm_length))
            l3 = Line(l2@1, (inner_radius, arm_length))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

solid_body = solid_body - Pos(0, 0, arm_length/2) * Cylinder(hole_diameter/2, arm_length)

slot_box = Pos(outer_radius - slot_depth/2, 0, 0) * Box(slot_depth, slot_width, arm_length)
solid_body = solid_body - slot_box

num_knurl = int((arm_length - 2 * knurl_start_offset) // knurl_spacing) + 1
for i in range(num_knurl):
    z_pos = knurl_start_offset + i * knurl_spacing
    knurl_cyl = Pos(outer_radius - knurl_depth/2, 0, z_pos) * Rot(0, 90, 0) * Cylinder(knurl_diameter/2, knurl_depth)
    solid_body = solid_body - knurl_cyl

part = solid_body
part.name = "hollow_cylinder_with_slot_and_knurls"
export_step(part, "output.step")