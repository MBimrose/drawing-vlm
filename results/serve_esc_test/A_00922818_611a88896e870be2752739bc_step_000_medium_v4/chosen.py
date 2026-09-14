from build123d import *

plate_length = 80.0
plate_width = 35.0
plate_thickness = 8.0
corner_radius = 10.0
pocket_length = 40.0
pocket_width = 25.0
pocket_depth = 1.5
hole_diameter = 3.4
hole_spacing = 6.0
hole_rows = 2
hole_cols = 2
hole_offset_x = -plate_length/2 + 15.0
hole_offset_y = 0.0
slot_width = 1.5
slot_length = 6.0
slot_offset_x = plate_length/2 - 12.0
slot_offset_y = 0.0
chamfer_size = 0.5
fillet_radius = 2.9

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        RectangleRounded(plate_length, plate_width, corner_radius)
    extrude(amount=plate_thickness)

solid_body = p.part

bottom_face = solid_body.faces().sort_by(Axis.Y)[0]
solid_body = fillet(bottom_face.edges(), fillet_radius)

solid_body = solid_body - Pos(0, plate_thickness/2 - pocket_depth/2, 0) * Box(pocket_length, pocket_depth, pocket_width)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = hole_offset_x + (i - (hole_cols-1)/2) * hole_spacing
        z = hole_offset_y + (j - (hole_rows-1)/2) * hole_spacing
        solid_body = solid_body - Pos(x, plate_thickness/2, z) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, plate_thickness)

solid_body = solid_body - Pos(slot_offset_x, plate_thickness/2 - pocket_depth/2, slot_offset_y) * Box(slot_length, pocket_depth, slot_width)
solid_body = solid_body - Pos(slot_offset_x, plate_thickness/2 - pocket_depth/2, slot_offset_y) * Box(slot_width, pocket_depth, slot_length)

part = solid_body
part.name = "plate_with_pockets_holes_slots"
export_step(part, "output.step")