from build123d import *

plate_width = 80.0
plate_length = 80.0
plate_thickness = 8.0
rib_width = 50.0
rib_length = 50.0
rib_height = 4.0
central_hole_diameter = 20.0
corner_hole_diameter = 6.0
corner_hole_offset = 30.0
counterbore_radius = 3.0
counterbore_outer = 6.0
counterbore_depth = 2.0
chamfer_size = 1.0
slot_width = 4.0
slot_length = 20.0

solid = Box(plate_width, plate_length, plate_thickness)
solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_size)

rib = Pos(0, 0, plate_thickness) * Box(rib_width, rib_length, rib_height)
solid = solid + rib

total_height = plate_thickness + rib_height
solid = solid - Pos(0, 0, total_height / 2) * Cylinder(central_hole_diameter / 2, total_height + 10)

for x, y in [(corner_hole_offset, corner_hole_offset), (-corner_hole_offset, corner_hole_offset),
             (corner_hole_offset, -corner_hole_offset), (-corner_hole_offset, -corner_hole_offset)]:
    solid = solid - Pos(x, y, total_height / 2) * Cylinder(counterbore_radius, total_height + 10)
    solid = solid - Pos(x, y, total_height - counterbore_depth / 2) * Cylinder(counterbore_outer, counterbore_depth)

for x, y in [(0, plate_length / 2 - slot_length / 2), (0, -plate_length / 2 + slot_length / 2),
             (plate_width / 2 - slot_length / 2, 0), (-plate_width / 2 + slot_length / 2, 0)]:
    solid = solid - Pos(x, y, total_height / 2) * Box(slot_width, slot_length, total_height + 10)

part = solid
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")