from build123d import *

plate_width = 70.0
plate_length = 80.0
plate_thickness = 10.0
boss_diameter = 30.0
boss_height = 20.0
shaft_diameter = 15.0
shaft_length = 60.0
keyway_width = 4.0
keyway_depth = 6.0
keyway_length = 20.0
keyway_offset = 50.0
chamfer_size = 1.0
mount_hole_dia = 5.0
mount_hole_spacing = 30.0
rib_thickness = 3.0
rib_height = 5.0
rib_length = 50.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_width, plate_length, plate_thickness)
boss = Pos(0, 0, plate_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
shaft = Pos(0, 0, plate_thickness + boss_height + shaft_length/2) * Cylinder(shaft_diameter/2, shaft_length)
rib = Pos(0, 0, plate_thickness + rib_height/2) * Box(rib_length, rib_thickness, rib_height)

result = base + boss + shaft + rib

for x, y in [(-mount_hole_spacing/2, -mount_hole_spacing/2),
             (mount_hole_spacing/2, -mount_hole_spacing/2),
             (-mount_hole_spacing/2, mount_hole_spacing/2),
             (mount_hole_spacing/2, mount_hole_spacing/2)]:
    result = result - Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_dia/2, plate_thickness)

keyway = Pos(shaft_diameter/2 - keyway_depth/2, 0, keyway_offset) * Box(keyway_depth, keyway_width, keyway_length)
result = result - keyway

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_size)

part = result
part.name = "plate_with_boss_shaft_and_keyway"
export_step(part, "output.step")