from build123d import *

width = 80.0
height = 30.0
thickness = 5.0
slot_width = 5.0
slot_length = 15.0
slot_offset_y = -5.0
fillet_radius = 1.0
chamfer_distance = 1.0
hole_diameter = 4.0
hole_offset_x = 20.0
hole_offset_y = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-width/2, -height/2), (width/2, -height/2))
            l2 = Line(l1@1, (width/2, height/2 - 10))
            a1 = ThreePointArc(l2@1, (width/2 - 5, height/2), (width/2 - 15, height/2 - 10))
            l3 = Line(a1@1, (-width/2 + 15, height/2 - 10))
            a2 = ThreePointArc(l3@1, (-width/2 + 5, height/2), (-width/2, height/2 - 10))
            l4 = Line(a2@1, (-width/2, -height/2))
        make_face()
    extrude(amount=thickness)

solid = p.part

slot_cut = Pos(0, slot_offset_y, thickness/2) * Box(slot_width, slot_length, thickness)
solid = solid - slot_cut

slot_edges = solid.edges().filter_by(Axis.Y).sort_by(Axis.Z)[-2:]
solid = fillet(slot_edges, fillet_radius)

chamfer_edges = solid.edges().filter_by(Axis.Z).sort_by(Axis.Y)[:4]
solid = chamfer(chamfer_edges, chamfer_distance)

for x, y in [(-hole_offset_x, hole_offset_y), (hole_offset_x, hole_offset_y)]:
    solid = solid - Pos(x, y, thickness/2) * Cylinder(hole_diameter/2, thickness)

part = solid
part.name = "custom_plate"
export_step(part, "output.step")