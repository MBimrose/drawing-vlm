from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 5.0
hole_diameter = 7.0
hole_spacing = 40.0
hole_offset_x = 20.0
hole_offset_y = 0.0
fillet_radius = 2.0
chamfer_distance = 0.5
slot_length = 40.0
slot_width = 6.0
slot_spacing = 20.0
counterbore_diameter = 12.0
counterbore_depth = 3.0

solid_body = Box(plate_length, plate_width, plate_thickness)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

pocket = Pos(0, 0, plate_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

slot1 = Pos(0, slot_spacing/2, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness)
slot2 = Pos(0, -slot_spacing, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness)
solid_body = solid_body - slot1 - slot2

for x, y in [(-hole_spacing/2, hole_offset_y), (hole_spacing/2, hole_offset_y)]:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)
    solid_body = solid_body - Pos(x, y, plate_thickness - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

part = solid_body
part.name = "plate_with_pockets_slots_and_holes"
export_step(part, "output.step")