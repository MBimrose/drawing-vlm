from build123d import *

plate_width = 80.0
plate_height = 50.0
plate_thickness = 6.0
central_hole_diameter = 30.0
slot_width = 20.0
slot_height = 12.0
clearance_hole_diameter = 5.0
clearance_hole_spacing = 20.0
mount_hole_diameter = 6.0
mount_hole_offset = 12.0
rib_thickness = 4.0
rib_height = 25.0
chamfer_distance = 0.5

result = Box(plate_width, plate_thickness, plate_height)
result = result - Rot(90, 0, 0) * Cylinder(central_hole_diameter/2, plate_thickness)
result = result - Box(slot_width, plate_thickness, slot_height)

for x, z in [(-clearance_hole_spacing/2, -clearance_hole_spacing/2),
             (clearance_hole_spacing/2, -clearance_hole_spacing/2),
             (-clearance_hole_spacing/2, clearance_hole_spacing/2),
             (clearance_hole_spacing/2, clearance_hole_spacing/2)]:
    result = result - Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(clearance_hole_diameter/2, plate_thickness)

for x, z in [(-plate_width/2 + mount_hole_offset, 0), (plate_width/2 - mount_hole_offset, 0)]:
    result = result - Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, plate_thickness)

result = result + Pos(-plate_width/2 - rib_thickness/2, -plate_thickness/2 - rib_thickness/2, 0) * Box(rib_thickness, rib_thickness, rib_height)
result = result + Pos(plate_width/2 + rib_thickness/2, -plate_thickness/2 - rib_thickness/2, 0) * Box(rib_thickness, rib_thickness, rib_height)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

part = result
part.name = "plate_with_holes_and_ribs"
export_step(part, "output.step")