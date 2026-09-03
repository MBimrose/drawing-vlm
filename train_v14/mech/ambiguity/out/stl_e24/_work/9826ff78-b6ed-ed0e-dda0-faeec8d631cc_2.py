from build123d import *

lever_length = 80.0
lever_width = 20.0
lever_thickness = 10.0
tip_radius = lever_width / 2.0
hole_diameter = 7.5
hole_offset = 30.0
slot_width = 12.0
slot_height = 6.0
slot_offset = 5.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-lever_width/2, 0), (lever_width/2, 0))
            l2 = Line(l1@1, (lever_width/2, lever_length - tip_radius))
            arc = ThreePointArc(l2@1, (0, lever_length + tip_radius), (-lever_width/2, lever_length - tip_radius))
            l3 = Line(arc@1, l1@0)
        make_face()
    extrude(amount=lever_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

solid_body = solid_body - Pos(0, hole_offset + tip_radius, lever_thickness/2) * Cylinder(hole_diameter/2, lever_thickness + 1)
solid_body = solid_body - Pos(0, lever_length - slot_offset, lever_thickness/2) * Box(slot_width, slot_height, lever_thickness + 1)

part = solid_body
part.name = "lever"
export_step(part, "output.step")