from build123d import *

outer_radius = 45.0
inner_radius = 30.0
height = 70.0
rib_thickness = 5.0
rib_height = 30.0
rib_base_z = 20.0
fillet_radius = 3.0
hole_diameter = 6.0
hole_offset_z = 15.0

shell = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

top_face = shell.faces().sort_by(Axis.Z)[-1]
shell = fillet(top_face.edges(), fillet_radius)

bottom_face = shell.faces().sort_by(Axis.Z)[0]
shell = fillet(bottom_face.edges(), fillet_radius)

rib = Pos(inner_radius - rib_thickness/2, 0, rib_base_z) * Box(rib_thickness, 2*outer_radius, rib_height)
pocket = Pos(inner_radius - rib_thickness/2, 0, rib_base_z + rib_height/2) * Box(rib_thickness*0.8, rib_height*0.6, rib_height*0.4)
rib = rib - pocket

combined = shell + rib

hole1 = Pos(outer_radius - hole_diameter/2, 0, hole_offset_z - height/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, 2*outer_radius)
hole2 = Pos(-(outer_radius - hole_diameter/2), 0, hole_offset_z - height/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, 2*outer_radius)

result = combined - hole1 - hole2

part = result
part.name = "shell_with_rib_and_holes"
export_step(part, "output.step")