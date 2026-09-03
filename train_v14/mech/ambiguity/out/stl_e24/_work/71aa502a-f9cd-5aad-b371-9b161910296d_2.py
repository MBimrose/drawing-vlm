from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 8.0
rib_height = 6.0
rib_thickness = 4.0
hole_diameter = 7.0
hole_spacing = 60.0
counterbore_diameter = 10.0
counterbore_depth = 2.0
blind_hole_diameter = 4.0
blind_hole_depth = 2.0
chamfer_distance = 1.0

base = Box(bracket_length, bracket_width, bracket_thickness)
rib = Pos(0, bracket_width/2 + rib_height/2, 0) * Box(bracket_length, rib_height, rib_thickness)
rib_mirror = mirror(rib, about=Plane.XZ)
result = base + rib + rib_mirror

for x in [-hole_spacing/2, hole_spacing/2]:
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter/2, bracket_thickness + 10)
    result = result - Pos(x, 0, bracket_thickness/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

result = result - Pos(0, 0, bracket_thickness/2 - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_distance)

part = result
part.name = "bracket"
export_step(part, "output.step")