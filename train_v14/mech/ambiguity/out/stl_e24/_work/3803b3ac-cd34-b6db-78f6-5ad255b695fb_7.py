from build123d import *

plate_length = 80.0
plate_width = 30.0
plate_thickness = 6.0
boss_radius = 12.0
boss_height = 5.0
slot_width = 6.0
slot_length = 20.0
hole_diameter = 4.0
hole_offset_x = 20.0
hole_offset_y = 6.0
chamfer_size = 0.5

solid = Box(plate_length, plate_width, plate_thickness)
solid = solid + Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)
solid = solid - Pos(plate_length/2 - slot_width/2, 0, 0) * Box(slot_width, slot_length, plate_thickness)
solid = solid - Pos(-plate_length/2 + slot_width/2, 0, 0) * Box(slot_width, slot_length, plate_thickness)

hole_positions = [
    (hole_offset_x, hole_offset_y),
    (hole_offset_x, -hole_offset_y),
    (-hole_offset_x, hole_offset_y),
    (-hole_offset_x, -hole_offset_y),
]
for x, y in hole_positions:
    solid = solid - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = chamfer(top_face.edges(), chamfer_size)

part = solid
part.name = "plate_with_boss_slots_holes"
export_step(part, "output.step")