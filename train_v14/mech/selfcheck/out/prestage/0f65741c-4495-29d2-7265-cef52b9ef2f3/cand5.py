from build123d import *

width = 80.0
depth = 30.0
thickness = 5.0
arc_height = 8.0
slot_width = 5.0
slot_length = 15.0
slot_offset_y = -5.0
hole_diameter = 4.0
hole_spacing = 40.0
hole_offset_y = 5.0
chamfer_size = 1.0
fillet_radius = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-width/2, -depth/2), (width/2, -depth/2))
            l2 = Line(l1@1, (width/2, depth/2 - arc_height))
            a1 = ThreePointArc(l2@1, (width/2 - arc_height/2, depth/2), (width/2 - arc_height, depth/2 - arc_height))
            l3 = Line(a1@1, (-width/2 + arc_height, depth/2 - arc_height))
            a2 = ThreePointArc(l3@1, (-width/2 + arc_height/2, depth/2), (-width/2, depth/2 - arc_height))
            l4 = Line(a2@1, (-width/2, -depth/2))
        make_face()
    extrude(amount=thickness)

solid_body = p.part

solid_body = solid_body - Pos(0, slot_offset_y, thickness/2) * Box(slot_width, slot_length, thickness)

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, hole_offset_y, thickness/2) * Cylinder(hole_diameter/2, thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

part = solid_body
part.name = "plate_with_arcs_slot_holes"
export_step(part, "output.step")