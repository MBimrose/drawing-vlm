from build123d import *

outer_radius = 20.0
inner_radius = 10.0
height = 70.0
groove_depth = 5.0
groove_width = 15.0
groove_start = 20.0
chamfer_size = 2.0
hole_diameter = 4.0
hole_offset = 12.0
slot_width = 5.0
slot_depth = 6.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, groove_start))
            l3 = Line(l2@1, (outer_radius - groove_depth, groove_start))
            l4 = Line(l3@1, (outer_radius - groove_depth, groove_start + groove_width))
            l5 = Line(l4@1, (outer_radius, groove_start + groove_width))
            l6 = Line(l5@1, (outer_radius, height))
            l7 = Line(l6@1, (inner_radius, height))
            l8 = Line(l7@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

hole_cyl = Pos(hole_offset, 0, height / 2) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, outer_radius * 2)
solid_body = solid_body - hole_cyl

slot_box = Pos(inner_radius - slot_depth / 2, 0, height / 2) * Box(slot_depth, slot_width, height)
solid_body = solid_body - slot_box

part = solid_body
part.name = "revolved_part_with_groove_hole_slot"
export_step(part, "output.step")