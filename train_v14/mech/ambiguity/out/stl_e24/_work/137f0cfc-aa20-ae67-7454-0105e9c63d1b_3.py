from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
central_hole_dia = 30.0
tab_width = 20.0
tab_height = 15.0
fillet_radius = 1.0
mount_hole_dia = 10.0
mount_hole_spacing = 30.0
rib_width = 5.0
rib_height = 2.0

result = Box(plate_length, plate_width, plate_thickness)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = fillet(top_face.edges(), fillet_radius)

result = result - Cylinder(central_hole_dia/2, plate_thickness)

tab = Pos(0, plate_width/2 + tab_height/2, 0) * Box(tab_width, tab_height, plate_thickness)
result = result + tab

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    result = result - Pos(x, 0, 0) * Cylinder(mount_hole_dia/2, plate_thickness)

rib = Pos(0, -plate_width/4, -plate_thickness/2 - rib_height/2) * Box(rib_width, plate_width/2, rib_height)
result = result + rib

part = result
part.name = "plate_with_tab_and_rib"
export_step(part, "output.step")