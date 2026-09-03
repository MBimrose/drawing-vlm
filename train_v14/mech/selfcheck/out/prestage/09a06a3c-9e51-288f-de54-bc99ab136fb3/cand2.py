from build123d import *

knob_width = 50.0
knob_height = 20.0
knob_depth = 16.0
wall_thickness = 2.0
chamfer_size = 1.0
central_hole_diameter = 6.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0
pocket_width = 12.0
pocket_height = 4.0
pocket_depth = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-knob_width/2, -knob_depth/2), (knob_width/2, -knob_depth/2))
            a1 = ThreePointArc(l1@1, (knob_width/2 + knob_depth/2, 0), (knob_width/2, knob_depth/2))
            l2 = Line(a1@1, (-knob_width/2, knob_depth/2))
            a2 = ThreePointArc(l2@1, (-knob_width/2 - knob_depth/2, 0), (-knob_width/2, -knob_depth/2))
        make_face()
    extrude(amount=knob_height)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, knob_height) * Cylinder(central_hole_diameter/2, knob_height + 1)
solid_body = solid_body - Pos(0, 0, knob_height) * Box(pocket_width, pocket_height, pocket_depth)
for x in [mount_hole_spacing/2, -mount_hole_spacing]:
    solid_body = solid_body - Pos(x, 0, knob_height/2) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, knob_depth + 1)
top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "knob"
export_step(part, "output.step")