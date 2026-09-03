from build123d import *

outer_width = 80.0
outer_height = 60.0
thickness = 12.0
wall_thickness = 5.0
top_radius = 12.0
slot_width = 6.0
slot_length = 30.0
slot_depth = 3.0
mount_hole_dia = 5.0
mount_hole_spacing = 40.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-outer_width/2, -outer_height/2), (outer_width/2, -outer_height/2))
            l2 = Line(l1@1, (outer_width/2, outer_height/2 - top_radius))
            arc = ThreePointArc(l2@1, (0, outer_height/2 + top_radius), (-outer_width/2, outer_height/2 - top_radius))
            l3 = Line(arc@1, l1@0)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - 2 * wall_thickness
inner_depth = thickness - wall_thickness

with BuildPart() as cp:
    with BuildSketch() as csk:
        with BuildLine() as cbl:
            cl1 = Line((-inner_width/2, -inner_height/2), (inner_width/2, -inner_height/2))
            cl2 = Line(cl1@1, (inner_width/2, inner_height/2 - top_radius))
            carc = ThreePointArc(cl2@1, (0, inner_height/2 + top_radius), (-inner_width/2, inner_height/2 - top_radius))
            cl3 = Line(carc@1, cl1@0)
        make_face()
    extrude(amount=inner_depth)

cavity = Pos(0, 0, wall_thickness) * cp.part
solid_body = solid_body - cavity

slot = Pos(0, 0, slot_depth/2) * Box(slot_width, slot_length, slot_depth)
solid_body = solid_body - slot

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(x, 0, thickness/2) * Cylinder(mount_hole_dia/2, thickness)
    solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "rounded_box_with_cavity"
export_step(part, "output.step")