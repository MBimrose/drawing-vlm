from build123d import *

outer_width = 80.0
outer_height = 40.0
thickness = 20.0
wall_thickness = 4.0
slot_width = 12.0
slot_depth = 6.0
chamfer_size = 1.0
hole_diameter = 6.0
hole_spacing = 24.0
hole_offset_x = 30.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-outer_width/2, -outer_height/2), (outer_width/2 - wall_thickness, -outer_height/2))
            a1 = ThreePointArc(l1@1, (outer_width/2, -outer_height/2), (outer_width/2, -outer_height/2 + wall_thickness))
            l2 = Line(a1@1, (outer_width/2, outer_height/2))
            l3 = Line(l2@1, (-outer_width/2, outer_height/2))
            l4 = Line(l3@1, l1@0)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

slot_box = Pos(outer_width/2 - slot_depth/2, 0, thickness/2) * Box(slot_depth, slot_width, thickness)
solid_body = solid_body - slot_box

z_edges = solid_body.edges().filter_by(Axis.Z)
pos_x_edges = [e for e in z_edges if e.center().X > 0]
solid_body = chamfer(pos_x_edges, chamfer_size)

for y in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(hole_offset_x, y, thickness/2) * Cylinder(hole_diameter/2, thickness)
    solid_body = solid_body - hole

part = solid_body
part.name = "custom_profile_with_slot_and_holes"
export_step(part, "output.step")