from build123d import *

outer_diameter = 80.0
inner_diameter = 20.0
thickness = 8.0
keyway_width = 6.0
keyway_depth = 4.0
set_screw_diameter = 4.0
set_screw_head_diameter = 7.0
set_screw_head_depth = 4.0
chamfer_size = 0.8

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
        Circle(inner_diameter / 2, mode=Mode.SUBTRACT)
    extrude(amount=thickness)

solid_body = p.part

keyway_box = Box(keyway_width, keyway_depth, thickness)
keyway_box = Pos(outer_diameter / 2 - keyway_depth / 2, 0, thickness / 2) * keyway_box
solid_body = solid_body - keyway_box

hole_x = outer_diameter / 2 - set_screw_head_diameter / 2 - 1.0
shaft_hole = Cylinder(set_screw_diameter / 2, thickness)
shaft_hole = Pos(hole_x, 0, thickness / 2) * shaft_hole
solid_body = solid_body - shaft_hole

cbore_hole = Cylinder(set_screw_head_diameter / 2, set_screw_head_depth)
cbore_hole = Pos(hole_x, 0, thickness - set_screw_head_depth / 2) * cbore_hole
solid_body = solid_body - cbore_hole

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "flanged_disc_with_keyway"
export_step(part, "output.step")