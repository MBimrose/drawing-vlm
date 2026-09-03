from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 8.0
rib_height = 6.0
rib_width = 60.0
rib_thickness = 4.0
hole_diameter = 4.0
hole_depth = 6.0
mount_hole_diameter = 6.0
mount_hole_clearance = 7.0
mount_cbore_diameter = 10.0
mount_cbore_depth = 2.0
chamfer_size = 1.0

base = Pos(0, 0, bracket_thickness/2) * Box(bracket_length, bracket_width, bracket_thickness)
rib = Pos(0, bracket_width/2 + rib_height/2, bracket_thickness/2) * Box(rib_width, rib_height, rib_thickness)
result = base + rib

result = result - Pos(0, 0, bracket_thickness) * Cylinder(hole_diameter/2, hole_depth)

mount_positions = [(-bracket_length/2 + 10, 0), (bracket_length/2 - 10, 0)]
for x, y in mount_positions:
    result = result - Pos(x, y, bracket_thickness) * CounterBoreHole(mount_hole_clearance/2, mount_cbore_diameter/2, mount_cbore_depth, bracket_thickness)

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_size)

part = result
part.name = "bracket_with_rib"
export_step(part, "output.step")