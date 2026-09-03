from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 10.0
slot_length = 30.0
slot_width = 6.0
slot_offset_y = 10.0
mount_hole_diameter = 4.5
mount_hole_head_diameter = 8.6
mount_hole_head_angle = 90
mount_hole_spacing = 50.0
rib_height = 4.0
rib_width = 8.0
rib_length = plate_length - 20.0
chamfer_size = 0.8

result = Box(plate_length, plate_width, plate_thickness)

slot = Pos(0, slot_offset_y, 0) * Box(slot_length, slot_width, plate_thickness)
result = result - slot

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(x, 0, -plate_thickness/2) * CounterSinkHole(mount_hole_diameter/2, mount_hole_head_diameter/2, plate_thickness, mount_hole_head_angle)
    result = result - hole

rib = Pos(0, 0, -plate_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
result = result + rib

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

part = result
part.name = "plate_with_slot_holes_rib"
export_step(part, "output.step")