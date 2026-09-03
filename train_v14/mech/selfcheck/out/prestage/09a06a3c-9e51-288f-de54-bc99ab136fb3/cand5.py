from build123d import *

knob_width = 70.0
knob_height = 25.0
knob_depth = 20.0
wall_thickness = 2.0
fillet_radius = 5.0
thread_hole_diameter = 6.0
thread_hole_depth = 15.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0
rib_width = 10.0
rib_height = 5.0
rib_thickness = 3.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-knob_width/2 + fillet_radius, -knob_height/2), (knob_width/2 - fillet_radius, -knob_height/2))
            a1 = ThreePointArc(l1@1, (knob_width/2, -knob_height/2 + fillet_radius), (knob_width/2, 0))
            a2 = ThreePointArc(a1@1, (knob_width/2, knob_height/2 - fillet_radius), (knob_width/2 - fillet_radius, knob_height/2))
            l2 = Line(a2@1, (-knob_width/2 + fillet_radius, knob_height/2))
            a3 = ThreePointArc(l2@1, (-knob_width/2, knob_height/2 - fillet_radius), (-knob_width/2, 0))
            a4 = ThreePointArc(a3@1, (-knob_width/2, -knob_height/2 + fillet_radius), (-knob_width/2 + fillet_radius, -knob_height/2))
        make_face()
    extrude(amount=knob_depth)

solid_body = p.part
solid_body = offset(solid_body, amount=-wall_thickness)

rib = Pos(0, 0, knob_depth - rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

thread_hole = Pos(0, 0, knob_depth - thread_hole_depth/2) * Cylinder(thread_hole_diameter/2, thread_hole_depth)
solid_body = solid_body - thread_hole

for x in [mount_hole_spacing/2, knob_width - mount_hole_spacing/2]:
    mount_hole = Pos(x, 0, knob_depth/2) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, knob_height + 10)
    solid_body = solid_body - mount_hole

part = solid_body
part.name = "knob"
export_step(part, "output.step")