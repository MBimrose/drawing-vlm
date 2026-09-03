from build123d import *

width = 60.0
height = 45.0
thickness = 5.0
corner_radius = 4.0
slot_width = 30.0
slot_height = 10.0
slot_offset_y = 5.0
hole_diameter = 4.0
hole_spacing = 20.0
hole_offset_y = -10.0
chamfer_size = 0.8

with BuildPart() as p:
    with BuildSketch() as s:
        RectangleRounded(width, height, corner_radius)
    extrude(amount=thickness)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

slot_center_y = height/2 - slot_offset_y - slot_height/2
slot_cut = Pos(0, slot_center_y, thickness/2) * Box(slot_width, slot_height, thickness)
solid_body = solid_body - slot_cut

hole_center_y = hole_offset_y
for x in [-hole_spacing/2, hole_spacing/2]:
    hole_cut = Pos(x, hole_center_y, thickness/2) * Cylinder(hole_diameter/2, thickness)
    solid_body = solid_body - hole_cut

part = solid_body
part.name = "rounded_plate_with_slot_and_holes"
export_step(part, "output.step")