from build123d import *

plate_width = 80.0
plate_length = 80.0
plate_thickness = 8.0
central_hole_diameter = 20.0
corner_padding = 10.0
corner_hole_diameter = 6.0
corner_cbore_diameter = 12.0
corner_cbore_depth = 2.0
rib_width = 50.0
rib_length = 50.0
rib_height = 4.0
slot_width = 4.0
slot_length = 20.0
chamfer_size = 0.5

solid = Box(plate_width, plate_length, plate_thickness)
solid = solid - Cylinder(central_hole_diameter/2, plate_thickness)

corner_x = (plate_width - 2 * corner_padding) / 2
corner_y = (plate_length - 2 * corner_padding) / 2
for cx, cy in [(corner_x, corner_y), (-corner_x, corner_y), (corner_x, -corner_y), (-corner_x, -corner_y)]:
    solid = solid - Pos(cx, cy, 0) * Cylinder(corner_hole_diameter/2, plate_thickness)
    solid = solid - Pos(cx, cy, plate_thickness/2 - corner_cbore_depth/2) * Cylinder(corner_cbore_diameter/2, corner_cbore_depth)

solid = solid - Pos(0, plate_length/2 - slot_length/2, 0) * Box(slot_width, slot_length, plate_thickness)
solid = solid - Pos(0, -plate_length/2 + slot_length/2, 0) * Box(slot_width, slot_length, plate_thickness)
solid = solid - Pos(plate_width/2 - slot_length/2, 0, 0) * Box(slot_length, slot_width, plate_thickness)
solid = solid - Pos(-plate_width/2 + slot_length/2, 0, 0) * Box(slot_length, slot_width, plate_thickness)

solid = solid + Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(rib_width, rib_length, rib_height)

solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_size)

part = solid
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")