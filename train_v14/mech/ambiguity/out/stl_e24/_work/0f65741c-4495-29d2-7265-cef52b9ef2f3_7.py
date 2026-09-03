from build123d import *

width = 80.0
height = 30.0
thickness = 5.0
tab_width = 12.0
tab_height = 8.0
tab_radius = 4.0
slot_width = 5.0
slot_length = 15.0
hole_diameter = 4.0
hole_spacing = 40.0
hole_offset_y = 10.0
chamfer_size = 1.0
fillet_radius = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-width/2, -height/2), (width/2, -height/2))
            l2 = Line(l1@1, (width/2, height/2 - tab_height))
            a1 = ThreePointArc(l2@1, (width/2 - tab_width/2, height/2), (width/2 - tab_width, height/2 - tab_height))
            l3 = Line(a1@1, (-width/2 + tab_width, height/2 - tab_height))
            a2 = ThreePointArc(l3@1, (-width/2 + tab_width/2, height/2), (-width/2, height/2 - tab_height))
            l4 = Line(a2@1, (-width/2, -height/2))
        make_face()
    extrude(amount=thickness)

solid_body = p.part

slot = Box(slot_width, slot_length, thickness)
solid_body = solid_body - Pos(0, 0, thickness/2) * slot

for x, y in [(-hole_spacing/2, hole_offset_y), (hole_spacing/2, hole_offset_y)]:
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(hole_diameter/2, thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)
solid_body = fillet(solid_body.edges().filter_by(Axis.X).sort_by(Axis.Z)[-2:], fillet_radius)

part = solid_body
part.name = "bracket_with_tabs"
export_step(part, "output.step")