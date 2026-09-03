from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_width = 10.0
rib_height = 6.0
hole_diameter = 12.0
chamfer_distance = 1.0
mount_hole_diameter = 5.0
mount_hole_spacing_x = 30.0
mount_hole_spacing_y = 20.0
pocket_depth = 2.0
pocket_margin = 2.0

result = Box(plate_length, plate_width, plate_thickness)

rib = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(plate_length, rib_width, rib_height)
result = result + rib

result = result - Cylinder(hole_diameter/2, plate_thickness + rib_height + 10)

for x, y in [(-mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (-mount_hole_spacing_x/2, mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, mount_hole_spacing_y/2)]:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness + rib_height + 10)

pocket = Pos(0, 0, -plate_thickness/2 + pocket_depth/2) * Box(plate_length - 2*pocket_margin, plate_width - 2*pocket_margin, pocket_depth)
result = result - pocket

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_distance)

part = result
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")