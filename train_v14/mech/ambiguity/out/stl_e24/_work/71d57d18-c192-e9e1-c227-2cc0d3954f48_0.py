from build123d import *

outer_radius = 30.0
inner_radius = 12.0
knob_height = 20.0
shoulder_height = 5.0
shoulder_radius = 22.0
fillet_radius = 3.0
chamfer_distance = 2.0
mount_hole_diameter = 4.0
mount_hole_offset = 18.0
slot_width = 6.0
slot_depth = 4.0
boss_radius = 4.0
boss_height = 8.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, knob_height - shoulder_height))
            l2 = Line(l1@1, (shoulder_radius, knob_height))
            l3 = Line(l2@1, (inner_radius, knob_height))
            l4 = Line(l3@1, (inner_radius, 0))
            l5 = Line(l4@1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

solid_body = solid_body - Pos(mount_hole_offset, 0, knob_height/2) * Cylinder(mount_hole_diameter/2, knob_height + 10)
solid_body = solid_body - Pos(-mount_hole_offset, 0, knob_height/2) * Cylinder(mount_hole_diameter/2, knob_height + 10)

slot_box = Pos(outer_radius - slot_depth/2, 0, knob_height/2) * Box(slot_depth, slot_width, knob_height)
solid_body = solid_body - slot_box

boss = Pos(inner_radius, 0, 0) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

part = solid_body
part.name = "knob"
export_step(part, "output.step")