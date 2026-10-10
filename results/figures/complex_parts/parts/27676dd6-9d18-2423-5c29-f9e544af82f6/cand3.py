from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
length = 100.0
rib_height = 5.0
rib_width = 20.0
rib_position = 40.0
counterbore_diameter = 60.0
counterbore_depth = 15.0
chamfer_size = 2.0
slot_width = 10.0
slot_length = 30.0
slot_depth = 5.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
rib_outer_radius = outer_radius + rib_height
rib_start = rib_position
rib_end = rib_position + rib_width

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, rib_start))
            l3 = Line(l2 @ 1, (rib_outer_radius, rib_start))
            l4 = Line(l3 @ 1, (rib_outer_radius, rib_end))
            l5 = Line(l4 @ 1, (outer_radius, rib_end))
            l6 = Line(l5 @ 1, (outer_radius, length))
            l7 = Line(l6 @ 1, (inner_radius, length))
            l8 = Line(l7 @ 1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = chamfer(solid_body.edges(), chamfer_size)

counterbore = Pos(0, 0, length - counterbore_depth / 2) * Cylinder(counterbore_diameter / 2, counterbore_depth)
solid_body = solid_body - counterbore

slot = Pos(outer_radius - slot_depth / 2, length / 2, length / 2) * Box(slot_depth, slot_length, slot_width)
solid_body = solid_body - slot

part = solid_body
part.name = "ribbed_cylinder_with_counterbore_and_slot"
export_step(part, "output.step")