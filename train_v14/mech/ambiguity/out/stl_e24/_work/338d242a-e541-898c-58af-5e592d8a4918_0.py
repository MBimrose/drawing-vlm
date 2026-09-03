from build123d import *

tube_length = 80.0
outer_radius = 12.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
slot_width = 4.0
slot_depth = 2.0
hole_diameter = 2.0
hole_spacing = 6.0
hole_offset = 12.0
hole_depth = 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, tube_length))
            l3 = Line(l2@1, (inner_radius, tube_length))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

slot_box = Pos(outer_radius - slot_depth/2, 0, 0) * Box(slot_depth, slot_width, tube_length)
solid_body = solid_body - slot_box

for i in range(10):
    z_pos = hole_offset + i * hole_spacing
    hole = Pos(outer_radius - hole_depth/2, 0, z_pos) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, hole_depth)
    solid_body = solid_body - hole

part = solid_body
part.name = "tube_with_slot_and_holes"
export_step(part, "output.step")