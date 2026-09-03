from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_height = 6.0
rib_width = 10.0
rib_margin = 2.0
central_hole_diameter = 12.0
mount_hole_diameter = 5.0
mount_hole_spacing_x = 30.0
mount_hole_spacing_y = 20.0
chamfer_distance = 1.0
pocket_depth = 3.0
pocket_margin = 2.0

rib_length = plate_length - 2 * rib_margin
total_height = plate_thickness + rib_height

result = Box(plate_length, plate_width, plate_thickness)
result = result + Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)

result = result - Pos(0, 0, rib_height/2) * Cylinder(central_hole_diameter/2, total_height)

for x, y in [(-mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (-mount_hole_spacing_x/2, mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, mount_hole_spacing_y/2)]:
    result = result - Pos(x, y, rib_height/2) * Cylinder(mount_hole_diameter/2, total_height)

pocket_w = plate_length - 2 * pocket_margin
pocket_h = plate_width - 2 * pocket_margin
result = result - Pos(0, 0, -plate_thickness/2 + pocket_depth/2) * Box(pocket_w, pocket_h, pocket_depth)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_distance)

part = result
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")