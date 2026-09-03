from build123d import *

arm_length = 80.0
outer_radius = 12.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
slot_width = 4.0
slot_length = 20.0
hole_diameter = 2.0
hole_spacing = 6.0
hole_count = 10
hole_depth = wall_thickness - 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, arm_length))
            l2 = Line(l1@1, (inner_radius, arm_length))
            l3 = Line(l2@1, (inner_radius, 0))
            l4 = Line(l3@1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

slot_cut = Pos(outer_radius - wall_thickness/2, 0, slot_length/2) * Box(wall_thickness, slot_width, slot_length)
solid_body = solid_body - slot_cut

for i in range(hole_count):
    z_pos = slot_length + hole_spacing/2 + i * hole_spacing
    hole_cut = Pos(outer_radius - hole_depth/2, 0, z_pos) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, hole_depth)
    solid_body = solid_body - hole_cut

part = solid_body
part.name = "hollow_cylinder_with_slot_and_holes"
export_step(part, "output.step")