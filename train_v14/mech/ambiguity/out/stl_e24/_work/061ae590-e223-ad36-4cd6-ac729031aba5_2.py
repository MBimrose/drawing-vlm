from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 8.0
boss_diameter = 12.0
boss_height = 6.0
hole_diameter = 16.0
hole_offset = 30.0
slot_width = 30.0
slot_depth = 10.0
slot_offset = 15.0
rib_width = 6.0
rib_thickness = 3.0
rib_height = 12.0
rib_spacing = 20.0
chamfer_size = 1.5

result = Box(plate_width, plate_depth, plate_thickness)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)
result = result + Pos(0, 0, plate_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)

for x, y in [(-hole_offset, -hole_offset), (hole_offset, hole_offset)]:
    result = result - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 10)

result = result - Pos(slot_offset, 0, plate_thickness/2) * Box(slot_width, slot_depth, plate_thickness + 10)

for x, y in [(-rib_spacing, -rib_spacing), (rib_spacing, -rib_spacing), (-rib_spacing, rib_spacing), (rib_spacing, rib_spacing)]:
    result = result + Pos(x, y, plate_thickness + rib_height/2) * Box(rib_width, rib_thickness, rib_height)

part = result
part.name = "plate_with_boss_holes_slot_ribs"
export_step(part, "output.step")