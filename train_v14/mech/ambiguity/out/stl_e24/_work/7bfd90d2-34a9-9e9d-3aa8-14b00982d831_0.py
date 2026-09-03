from build123d import *

outer_radius = 30.0
inner_radius = 8.0
height = 20.0
set_screw_diameter = 4.0
set_screw_depth = 8.0
set_screw_offset = 2.0
slot_width = 4.0
slot_depth = 6.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, height))
            l3 = Line(l2@1, (inner_radius, height))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = chamfer(solid_body.edges(), chamfer_size)

slot_box = Pos(outer_radius - slot_depth/2, 0, 0) * Box(slot_depth, slot_width, height)
solid_body = solid_body - slot_box

hole1 = Pos(outer_radius - set_screw_offset, set_screw_depth/2, height/2) * Rot(90, 0, 0) * Cylinder(set_screw_diameter/2, set_screw_depth)
solid_body = solid_body - hole1

hole2 = Pos(outer_radius - set_screw_offset, -set_screw_depth/2, height/2) * Rot(90, 0, 0) * Cylinder(set_screw_diameter/2, set_screw_depth)
solid_body = solid_body - hole2

part = solid_body
part.name = "knob_with_slot_and_set_screw_holes"
export_step(part, "output.step")