from build123d import *

outer_diameter = 80.0
inner_diameter = 60.0
length = 80.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
slot_width = 10.0
slot_height = 30.0
slot_depth = wall_thickness + 2.0
chamfer_size = 1.0
mount_hole_diameter = 5.0
mount_hole_spacing = 40.0

outer_cyl = Cylinder(outer_diameter / 2.0, length)
inner_cyl = Cylinder(inner_diameter / 2.0, length)
shell = outer_cyl - inner_cyl

slot = Pos(0, 0, slot_depth / 2.0) * Box(slot_height, length, slot_depth)
shell = shell - slot

for y in [-mount_hole_spacing / 2.0, mount_hole_spacing / 2.0]:
    hole = Pos(0, y, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2.0, length)
    shell = shell - hole

shell = chamfer(shell.edges(), chamfer_size)

part = shell
part.name = "hollow_cylinder_with_slot_and_mount_holes"
export_step(part, "output.step")