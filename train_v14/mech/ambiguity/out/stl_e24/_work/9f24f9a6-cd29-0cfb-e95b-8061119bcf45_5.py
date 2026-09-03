from build123d import *
import math

plate_length = 80.0
plate_width = 20.0
plate_thickness = 5.0
boss_diameter = 20.0
boss_height = 30.0
set_screw_diameter = 3.0
set_screw_head_diameter = 6.0
set_screw_head_angle = 90.0
mount_hole_diameter = 4.0
mount_hole_spacing = 40.0
rib_hole_diameter = 3.0
rib_hole_offset = 20.0
chamfer_size = 0.5

plate = Box(plate_length, plate_width, plate_thickness)
boss = Pos(0, 0, plate_thickness/2) * Cylinder(boss_diameter/2, boss_height)
result = plate + boss

csk_depth = (set_screw_head_diameter/2) / math.tan(math.radians(set_screw_head_angle/2))
shaft_depth = boss_height - csk_depth
csk_cone = Pos(0, 0, plate_thickness/2 + boss_height - csk_depth) * Cone(set_screw_diameter/2, set_screw_head_diameter/2, csk_depth)
shaft_cyl = Pos(0, 0, plate_thickness/2 + boss_height - csk_depth - shaft_depth) * Cylinder(set_screw_diameter/2, shaft_depth)
result = result - csk_cone - shaft_cyl

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    result = result - Pos(x, 0, 0) * Cylinder(mount_hole_diameter/2, plate_thickness + 10)

for x in [-rib_hole_offset, rib_hole_offset]:
    result = result - Pos(x, 0, 0) * Cylinder(rib_hole_diameter/2, plate_thickness + 10)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_boss_and_holes"
export_step(part, "output.step")