from build123d import *

knob_width = 60.0
knob_height = 20.0
knob_depth = 16.0
wall_thickness = 2.0
rib_width = 10.0
rib_height = 4.0
rib_depth = 3.0
blind_hole_diameter = 6.0
blind_hole_depth = 15.0
side_hole_diameter = 4.0
side_hole_spacing = 15.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-knob_width/2, -knob_depth/2), (knob_width/2, -knob_depth/2))
            a1 = ThreePointArc(l1 @ 1, (knob_width/2 + wall_thickness, 0), (knob_width/2, knob_depth/2))
            l2 = Line(a1 @ 1, (-knob_width/2, knob_depth/2))
            a2 = ThreePointArc(l2 @ 1, (-knob_width/2 - wall_thickness, 0), (-knob_width/2, -knob_depth/2))
        make_face()
    extrude(amount=knob_height)

solid_body = p.part

rib = Pos(0, 0, knob_height) * Box(rib_width, rib_height, rib_depth)
solid_body = solid_body + rib

blind_hole = Pos(0, 0, knob_height - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)
solid_body = solid_body - blind_hole

for i in range(2):
    x_pos = knob_width/2 - wall_thickness - side_hole_spacing/2 + i * side_hole_spacing
    side_hole = Pos(x_pos, 0, knob_height/2) * Rot(90, 0, 0) * Cylinder(side_hole_diameter/2, knob_depth + 10)
    solid_body = solid_body - side_hole

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "knob"
export_step(part, "output.step")