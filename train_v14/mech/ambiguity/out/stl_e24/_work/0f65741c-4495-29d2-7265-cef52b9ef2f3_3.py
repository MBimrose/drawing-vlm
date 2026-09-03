from build123d import *

width = 80.0
height = 30.0
thickness = 5.0
corner_radius = 10.0
slot_width = 5.0
slot_length = 15.0
slot_offset_y = -5.0
hole_diameter = 4.0
hole_spacing = 40.0
hole_offset_y = 5.0
chamfer_distance = 1.0
fillet_radius = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-width/2, -height/2), (width/2, -height/2))
            l2 = Line(l1@1, (width/2, height/2 - corner_radius))
            a1 = ThreePointArc(l2@1, (width/2, height/2), (width/2 - corner_radius, height/2 - corner_radius))
            l3 = Line(a1@1, (-width/2 + corner_radius, height/2 - corner_radius))
            a2 = ThreePointArc(l3@1, (-width/2, height/2), (-width/2, height/2 - corner_radius))
            l4 = Line(a2@1, (-width/2, -height/2))
        make_face()
    extrude(amount=thickness)

solid_body = p.part

slot = Pos(0, slot_offset_y, thickness/2) * Box(slot_width, slot_length, thickness)
solid_body = solid_body - slot

for x in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(x, hole_offset_y, thickness/2) * Cylinder(hole_diameter/2, thickness)
    solid_body = solid_body - hole

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges().filter_by(Axis.X)
solid_body = fillet(top_edges, fillet_radius)

part = solid_body
part.name = "plate_with_slot_and_holes"
export_step(part, "output.step")