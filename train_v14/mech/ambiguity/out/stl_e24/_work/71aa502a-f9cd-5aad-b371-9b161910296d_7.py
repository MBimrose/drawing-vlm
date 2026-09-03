from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 8.0
rib_height = 6.0
rib_thickness = 4.0
blind_hole_diameter = 4.0
blind_hole_depth = 6.0
mount_hole_diameter = 6.0
mount_hole_clearance = 7.0
mount_hole_cbore_diameter = 10.0
mount_hole_cbore_depth = 4.0
mount_hole_spacing = 60.0
chamfer_distance = 1.0

base = Pos(0, 0, bracket_thickness/2) * Box(bracket_length, bracket_width, bracket_thickness)
rib = Pos(0, bracket_width/2 + rib_height/2, bracket_thickness/2) * Box(bracket_length, rib_height, bracket_thickness)
result = base + rib

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    result = result - Pos(x, 0, bracket_thickness - mount_hole_cbore_depth/2) * Cylinder(mount_hole_cbore_diameter/2, mount_hole_cbore_depth)
    result = result - Pos(x, 0, bracket_thickness/2) * Cylinder(mount_hole_clearance/2, bracket_thickness + 1)

result = result - Pos(0, 0, bracket_thickness - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_distance)

part = result
part.name = "bracket_with_rib"
export_step(part, "output.step")