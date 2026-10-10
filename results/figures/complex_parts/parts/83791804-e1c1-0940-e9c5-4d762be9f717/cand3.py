from build123d import *

plate_width = 80.0
plate_height = 50.0
plate_thickness = 5.0
central_hole_dia = 30.0
clearance_hole_dia = 5.0
clearance_spacing_x = 40.0
clearance_spacing_y = 12.0
mount_hole_dia = 6.0
mount_hole_spacing = 20.0
rib_width = 4.0
rib_height = 30.0
chamfer_size = 0.5

result = Box(plate_width, plate_thickness, plate_height)
result = result - Rot(90, 0, 0) * Cylinder(central_hole_dia/2, plate_thickness)

for x, z in [(-clearance_spacing_x/2, -clearance_spacing_y/2),
             (clearance_spacing_x/2, -clearance_spacing_y/2),
             (-clearance_spacing_x/2, clearance_spacing_y/2),
             (clearance_spacing_x/2, clearance_spacing_y/2)]:
    result = result - Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(clearance_hole_dia/2, plate_thickness)

for x, z in [(-mount_hole_spacing/2, 0), (mount_hole_spacing/2, 0)]:
    result = result - Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(mount_hole_dia/2, plate_thickness)

result = result + Pos(-plate_width/2 - rib_width/2, 0, 0) * Box(rib_width, plate_thickness, rib_height)
result = result + Pos(plate_width/2 + rib_width/2, 0, 0) * Box(rib_width, plate_thickness, rib_height)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")