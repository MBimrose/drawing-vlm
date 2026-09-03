from build123d import *

bracket_length = 80
bracket_width = 40
bracket_thickness = 8
central_hole_diameter = 20
counterbore_diameter = 30
counterbore_depth = 4
slot_width = 8
slot_length = bracket_length - 10
mount_hole_diameter = 4
mount_hole_spacing = 24
rib_width = 6
rib_length = 20
rib_height = 4
chamfer_distance = 1

result = Box(bracket_length, bracket_width, bracket_thickness)
result = result - Cylinder(central_hole_diameter/2, bracket_thickness)
result = result - Pos(0, 0, bracket_thickness/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
result = result - Box(slot_length, slot_width, bracket_thickness)
for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    result = result - Pos(0, y, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, bracket_length)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)
rib1 = Pos(-bracket_length/2 + rib_length/2 + 5, 0, bracket_thickness + rib_height/2) * Box(rib_width, rib_length, rib_height)
rib2 = Pos(bracket_length/2 - rib_length/2 - 5, 0, bracket_thickness + rib_height/2) * Box(rib_width, rib_length, rib_height)
result = result + rib1 + rib2

part = result
part.name = "bracket"
export_step(part, "output.step")