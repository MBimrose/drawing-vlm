from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
length = 100.0
rib_height = 5.0
rib_width = 20.0
rib_position = 40.0
slot_width = 12.0
slot_height = 30.0
slot_depth = 8.0
chamfer_size = 2.0
mount_hole_dia = 6.0
mount_hole_spacing = 40.0
pocket_depth = 10.0
pocket_dia = 60.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
rib_outer_radius = outer_radius + rib_height

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, rib_position))
            l3 = Line(l2 @ 1, (rib_outer_radius, rib_position))
            l4 = Line(l3 @ 1, (rib_outer_radius, rib_position + rib_width))
            l5 = Line(l4 @ 1, (outer_radius, rib_position + rib_width))
            l6 = Line(l5 @ 1, (outer_radius, length))
            l7 = Line(l6 @ 1, (0, length))
            l8 = Line(l7 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, length / 2) * Cylinder(inner_radius, length)
solid_body = solid_body - Pos(0, 0, length - pocket_depth / 2) * Cylinder(pocket_dia / 2, pocket_depth)
solid_body = chamfer(solid_body.edges(), chamfer_size)

slot_box = Pos(outer_radius - slot_depth / 2, length / 2, 0) * Box(slot_depth, slot_width, slot_height)
solid_body = solid_body - slot_box

for x, y in [(mount_hole_spacing / 2, 0), (-mount_hole_spacing / 2, 0)]:
    solid_body = solid_body - Pos(x, y, length / 2) * Cylinder(mount_hole_dia / 2, length)

part = solid_body
part.name = "ribbed_cylinder_with_slot"
export_step(part, "output.step")