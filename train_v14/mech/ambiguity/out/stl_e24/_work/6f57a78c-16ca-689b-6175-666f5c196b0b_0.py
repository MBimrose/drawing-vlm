from build123d import *

outer_diameter = 80.0
inner_diameter = 60.0
length = 80.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
slot_width = 10.0
slot_depth = 20.0
chamfer_size = 1.0
mount_hole_diameter = 5.0
mount_hole_offset = 30.0

outer_cyl = Cylinder(outer_diameter / 2.0, length)
inner_cyl = Cylinder(inner_diameter / 2.0, length)
shell = outer_cyl - inner_cyl

slot = Pos(0, 0, slot_width / 2.0) * Box(slot_depth, outer_diameter, slot_width)
shell = shell - slot

hole1 = Pos(0, mount_hole_offset, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2.0, wall_thickness + 2.0)
hole2 = Pos(0, -mount_hole_offset, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2.0, wall_thickness + 2.0)
shell = shell - hole1 - hole2

shell = chamfer(shell.edges(), chamfer_size)

part = shell
part.name = "hollow_cylinder_with_slot_and_holes"
export_step(part, "output.step")