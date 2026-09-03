from build123d import *

plate_width = 80.0
plate_height = 70.0
plate_thickness = 4.0
pocket_width = 30.0
pocket_height = 20.0
slot_length = 50.0
slot_width = 5.0
hole_diameter = 5.5
hole_spacing_x = 20.0
hole_spacing_y = 15.0
hole_rows = 3
hole_cols = 2
chamfer_size = 0.5
rib_width = 10.0
rib_height = 30.0

solid_body = Box(plate_width, plate_height, plate_thickness)
solid_body = solid_body - Box(pocket_width, pocket_height, plate_thickness)

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness)
slot_solid = Pos(0, -plate_height/4, -plate_thickness/2) * slot_bp.part
solid_body = solid_body - slot_solid

for i in range(hole_cols):
    for j in range(hole_rows):
        x = i * hole_spacing_x
        y = j * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

rib = Pos(-plate_width/2 + rib_width/2, 0, 0) * Box(rib_width, rib_height, plate_thickness)
solid_body = solid_body + rib

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "plate_with_pocket_slot_holes_rib"
export_step(part, "output.step")