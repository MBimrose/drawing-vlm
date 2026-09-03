from build123d import *

width = 40.0
depth = 12.0
thickness = 4.0
rib_width = 6.0
rib_height = 2.0
rib_offset = 5.0
hole_diameter = 3.3
hole_x = 30.0
hole_y = 6.0
slot_width = 2.0
slot_length = 6.0
slot_center_x = 10.0
chamfer_distance = 0.5

base = Pos(0.5 * width, 0, 0.5 * thickness) * Box(width, depth, thickness)
rib = Pos(rib_offset, 0, 0.5 * rib_height) * Box(rib_width, depth, rib_height)
result = base + rib

hole = Pos(hole_x, hole_y - 0.5 * depth, 0) * Cylinder(hole_diameter / 2, thickness + 10)
result = result - hole

slot = Pos(slot_center_x, 0.5 * depth - 0.5 * slot_length, 0) * Box(slot_width, slot_length, thickness + 10)
result = result - slot

right_face = result.faces().sort_by(Axis.X)[-1]
result = chamfer(right_face.edges(), chamfer_distance)

part = result
part.name = "ribbed_plate_with_hole_and_slot"
export_step(part, "output.step")