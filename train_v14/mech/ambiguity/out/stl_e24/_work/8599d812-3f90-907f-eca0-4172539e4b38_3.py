from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 4.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 2.0
mount_hole_dia = 3.0
mount_hole_offset = 5.0
rib_thickness = 2.0
rib_height = 2.0
chamfer_size = 0.5

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

pocket = Box(pocket_length, pocket_width, pocket_depth)
base = base - pocket

hole_r = mount_hole_dia / 2
hole_h = plate_thickness + 1.0
for x in [-(plate_length/2 - mount_hole_offset), plate_length/2 - mount_hole_offset]:
    for y in [-(plate_width/2 - mount_hole_offset), plate_width/2 - mount_hole_offset]:
        base = base - Pos(x, y, 0) * Cylinder(hole_r, hole_h)

rib = Box(plate_length - 2*mount_hole_offset, rib_thickness, rib_height)
part = base + rib
part.name = "plate_with_pocket_holes_and_rib"
export_step(part, "output.step")