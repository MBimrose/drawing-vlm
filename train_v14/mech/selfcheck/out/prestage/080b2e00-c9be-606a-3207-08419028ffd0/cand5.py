from build123d import *

plate_width = 60.0
plate_depth = 45.0
plate_thickness = 5.0
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
        Rectangle(plate_width, plate_depth)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_radius)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

slot_cut = Pos(0, slot_offset_y, plate_thickness/2) * Box(slot_width, slot_height, plate_thickness)
solid_body = solid_body - slot_cut

for x in [-hole_spacing/2, hole_spacing/2]:
    hole_cut = Pos(x, hole_offset_y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)
    solid_body = solid_body - hole_cut

part = solid_body
part.name = "plate_with_slot_and_holes"
export_step(part, "output.step")