from build123d import *

outer_diameter = 60.0
inner_diameter = 12.0
thickness = 15.0
rib_height = 2.0
rib_width = 5.0
chamfer_size = 1.0
mount_hole_diameter = 4.0
mount_hole_offset = 20.0
central_recess_diameter = 8.0
central_recess_depth = 3.0

base = Cylinder(outer_diameter / 2, thickness)
base = chamfer(base.edges(), chamfer_size)

rib = Cylinder(outer_diameter / 2, rib_height) - Cylinder((outer_diameter / 2) - rib_width, rib_height)
rib = Pos(0, 0, thickness / 2 - rib_height / 2) * rib

result = base + rib

result = result - Pos(0, 0, thickness / 2) * Cylinder(inner_diameter / 2, thickness + 1)

for x, y in [(mount_hole_offset, mount_hole_offset), (-mount_hole_offset, mount_hole_offset),
             (-mount_hole_offset, -mount_hole_offset), (mount_hole_offset, -mount_hole_offset)]:
    result = result - Pos(x, y, thickness / 2) * Cylinder(mount_hole_diameter / 2, thickness + 1)

result = result - Pos(0, 0, thickness / 2 - central_recess_depth / 2) * Cylinder(central_recess_diameter / 2, central_recess_depth)

part = result
part.name = "ribbed_disc_with_holes"
export_step(part, "output.step")