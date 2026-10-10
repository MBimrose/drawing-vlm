from build123d import *

outer_diameter = 40.0
inner_diameter = 20.0
length = 70.0
groove_width = 15.0
groove_depth = 5.0
groove_position = 10.0
chamfer_size = 2.0
hole_diameter = 4.0
hole_offset = 20.0
slot_width = 5.0
slot_depth = 8.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, groove_position))
            l3 = Line(l2@1, (outer_radius - groove_depth, groove_position))
            l4 = Line(l3@1, (outer_radius - groove_depth, groove_position + groove_width))
            l5 = Line(l4@1, (outer_radius, groove_position + groove_width))
            l6 = Line(l5@1, (outer_radius, length))
            l7 = Line(l6@1, (inner_radius, length))
            l8 = Line(l7@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

hole_cyl = Pos(0, 0, hole_offset) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2.0, outer_diameter)
solid_body = solid_body - hole_cyl

slot_box = Pos(inner_radius, 0, length / 2.0) * Box(slot_width, slot_depth, length)
solid_body = solid_body - slot_box

part = solid_body
part.name = "revolved_tube_with_groove_hole_slot"
export_step(part, "output.step")