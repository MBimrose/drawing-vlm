from build123d import *

knob_length = 50.0
knob_height = 20.0
knob_width = 16.0
wall_thickness = 2.0
central_hole_diameter = 6.0
mount_hole_diameter = 4.0
mount_hole_spacing = 15.0
mount_hole_offset = 12.0
pocket_width = 10.0
pocket_height = 4.0
pocket_depth = 2.0
fillet_radius = 0.5

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((-knob_length/2, -knob_height/2), (-knob_length/2, knob_height/2))
            a1 = ThreePointArc(l1@1, (-knob_length/2 - knob_width/2, 0), (-knob_length/2, -knob_height/2))
            l2 = Line(a1@1, (knob_length/2, -knob_height/2))
            a2 = ThreePointArc(l2@1, (knob_length/2 + knob_width/2, 0), (knob_length/2, knob_height/2))
            l3 = Line(a2@1, (-knob_length/2, knob_height/2))
        make_face()
    extrude(amount=knob_width)

solid_body = p.part

solid_body = solid_body - Pos(0, knob_width/2, knob_height/2) * Cylinder(central_hole_diameter/2, knob_height + 1)

for x in [mount_hole_offset, mount_hole_offset + mount_hole_spacing]:
    solid_body = solid_body - Pos(x, knob_width/2, 0) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, knob_width + 1)

solid_body = solid_body - Pos(0, knob_width/2, knob_height/2) * Box(pocket_width, pocket_height, pocket_depth)

pocket_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-4:]
solid_body = fillet(pocket_edges, fillet_radius)

part = solid_body
part.name = "knob"
export_step(part, "output.step")