from build123d import *

plate_width = 70.0
plate_length = 80.0
plate_thickness = 10.0
boss_diameter = 30.0
boss_height = 20.0
shaft_diameter = 15.0
shaft_length = 60.0
slot_width = 12.0
slot_length = 20.0
chamfer_size = 1.0
mount_hole_dia = 5.0
mount_hole_spacing = 30.0
rib_thickness = 3.0
rib_height = 5.0
rib_offset = 10.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_width, plate_length, plate_thickness)
boss = Pos(0, 0, plate_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
shaft = Pos(0, 0, plate_thickness + boss_height + shaft_length/2) * Cylinder(shaft_diameter/2, shaft_length)
rib = Pos(0, 0, plate_thickness + rib_height/2) * Box(plate_width - 2*rib_offset, rib_thickness, rib_height)

result = base + boss + shaft + rib

slot = Pos(0, 0, plate_thickness + boss_height + shaft_length/2) * Box(shaft_diameter + 2, slot_width, slot_length)
result = result - slot

hole_positions = [
    (-mount_hole_spacing/2, -mount_hole_spacing/2),
    (mount_hole_spacing/2, -mount_hole_spacing/2),
    (-mount_hole_spacing/2, mount_hole_spacing/2),
    (mount_hole_spacing/2, mount_hole_spacing/2),
]
for x, y in hole_positions:
    result = result - Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_dia/2, plate_thickness + 1)

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_size)

part = result
part.name = "plate_with_boss_shaft_and_rib"
export_step(part, "output.step")