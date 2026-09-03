from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 8.0
central_hole_diameter = 20.0
countersink_diameter = 30.0
countersink_depth = 3.0
slot_width = 8.0
slot_length = 30.0
slot_offset = 20.0
mount_hole_diameter = 4.0
mount_hole_spacing = 24.0
rib_width = 6.0
rib_length = 20.0
rib_height = 4.0
chamfer_size = 1.0

result = Box(bracket_length, bracket_width, bracket_thickness)
result = result - Cylinder(central_hole_diameter/2, bracket_thickness)
result = result - Pos(0, 0, bracket_thickness/2 - countersink_depth/2) * Cylinder(countersink_diameter/2, countersink_depth)
result = result - Pos(-slot_offset, 0, 0) * Box(slot_length, slot_width, bracket_thickness)
result = result - Pos(slot_offset, 0, 0) * Box(slot_length, slot_width, bracket_thickness)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)
result = result - Pos(0, -mount_hole_spacing/2, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, bracket_length)
result = result - Pos(0, mount_hole_spacing/2, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, bracket_length)
result = result + Pos(-bracket_length/4, 0, bracket_thickness + rib_height/2) * Box(rib_width, rib_length, rib_height)
result = result + Pos(bracket_length/4, 0, bracket_thickness + rib_height/2) * Box(rib_width, rib_length, rib_height)

part = result
part.name = "bracket"
export_step(part, "output.step")