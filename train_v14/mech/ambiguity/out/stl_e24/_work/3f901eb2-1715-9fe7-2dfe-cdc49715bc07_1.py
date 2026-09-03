from build123d import *

plate_width = 80.0
plate_length = 80.0
plate_thickness = 8.0
boss_radius = 20.0
boss_height = 10.0
counterbore_diameter = 16.0
counterbore_depth = 4.0
through_hole_diameter = 4.0
mount_hole_diameter = 6.0
mount_hole_offset = 30.0
rib_width = 10.0
rib_height = 5.0
rib_thickness = 4.0
fillet_radius = 2.0
chamfer_distance = 0.5
slot_width = 10.0
slot_depth = 5.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_width, plate_length, plate_thickness)
boss = Pos(0, 0, plate_thickness + boss_height/2) * Cylinder(boss_radius, boss_height)
result = base + boss

top_face = result.faces().sort_by(Axis.Z)[-1]
result = fillet(top_face.edges(), fillet_radius)

cbore = Pos(0, 0, plate_thickness + boss_height - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
thru = Pos(0, 0, (plate_thickness + boss_height)/2) * Cylinder(through_hole_diameter/2, plate_thickness + boss_height + 10)
result = result - cbore - thru

for x, y in [(mount_hole_offset, mount_hole_offset), (-mount_hole_offset, mount_hole_offset),
             (-mount_hole_offset, -mount_hole_offset), (mount_hole_offset, -mount_hole_offset)]:
    result = result - Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_diameter/2, plate_thickness + 10)

for x, y in [(-plate_width/2 + rib_width/2, -plate_length/2 + rib_thickness/2),
             (plate_width/2 - rib_width/2, -plate_length/2 + rib_thickness/2),
             (-plate_width/2 + rib_width/2, plate_length/2 - rib_thickness/2),
             (plate_width/2 - rib_width/2, plate_length/2 - rib_thickness/2)]:
    result = result + Pos(x, y, rib_height/2) * Box(rib_width, rib_thickness, rib_height)

for x, y in [(-plate_width/2 + slot_width/2, -plate_length/2 + slot_depth/2),
             (plate_width/2 - slot_width/2, -plate_length/2 + slot_depth/2),
             (-plate_width/2 + slot_width/2, plate_length/2 - slot_depth/2),
             (plate_width/2 - slot_width/2, plate_length/2 - slot_depth/2)]:
    result = result - Pos(x, y, plate_thickness/2) * Box(slot_width, slot_depth, plate_thickness)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

part = result
part.name = "plate_with_boss_and_ribs"
export_step(part, "output.step")