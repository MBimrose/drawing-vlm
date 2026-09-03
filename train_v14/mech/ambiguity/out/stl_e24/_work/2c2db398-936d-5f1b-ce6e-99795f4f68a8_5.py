from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 8.0
edge_fillet_radius = 2.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
pocket_radius = 12.0
pocket_depth = 4.0
pocket_center_x = 20.0
pocket_center_y = 0.0

solid_body = Box(plate_width, plate_depth, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), edge_fillet_radius)

hole_r = mount_hole_diameter / 2
hole_h = plate_thickness + 2
for x in [-plate_width/2 + mount_hole_offset, plate_width/2 - mount_hole_offset]:
    for y in [-plate_depth/2 + mount_hole_offset, plate_depth/2 - mount_hole_offset]:
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_r, hole_h)

pocket_cyl = Pos(pocket_center_x, pocket_center_y, plate_thickness/2 - pocket_depth/2) * Cylinder(pocket_radius, pocket_depth)
solid_body = solid_body - pocket_cyl

part = solid_body
part.name = "plate_with_holes_and_pocket"
export_step(part, "output.step")