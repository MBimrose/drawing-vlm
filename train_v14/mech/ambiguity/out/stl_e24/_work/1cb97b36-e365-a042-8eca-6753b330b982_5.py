from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
t_slot_width = 6.0
t_slot_depth = 20.0
t_slot_top_width = 30.0
t_slot_top_thickness = 6.0
gusset_width = 12.0
gusset_height = 30.0
mount_hole_diameter = 4.0
mount_hole_spacing = 60.0

base = Box(plate_length, plate_width, plate_thickness)

vertical_slot = Box(t_slot_width, t_slot_depth, plate_thickness)
horizontal_slot = Pos(0, t_slot_depth/2 + t_slot_top_thickness/2, 0) * Box(t_slot_top_width, t_slot_top_thickness, plate_thickness)
t_slot = vertical_slot + horizontal_slot
base = base - t_slot

left_gusset = Pos(-plate_length/2 - gusset_width/2, 0, plate_thickness/2) * Box(gusset_width, gusset_height, plate_thickness)
right_gusset = Pos(plate_length/2 + gusset_width/2, 0, plate_thickness/2) * Box(gusset_width, gusset_height, plate_thickness)
base = base + left_gusset + right_gusset

hole1 = Pos(-mount_hole_spacing/2, 0, 0) * Cylinder(mount_hole_diameter/2, plate_thickness)
hole2 = Pos(mount_hole_spacing/2, 0, 0) * Cylinder(mount_hole_diameter/2, plate_thickness)
base = base - hole1 - hole2

part = base
part.name = "plate_with_t_slot_and_gussets"
export_step(part, "output.step")