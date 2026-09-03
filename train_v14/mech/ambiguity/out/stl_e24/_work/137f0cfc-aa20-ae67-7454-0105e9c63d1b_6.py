from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 5.0
tab_width = 20.0
tab_height = 15.0
cutout_diameter = 30.0
mount_hole_diameter = 10.0
mount_hole_spacing = 30.0
fillet_radius = 1.0
rib_width = 5.0
rib_height = 20.0
rib_thickness = 2.0
rib_offset_y = -plate_height/4

result = Box(plate_width, plate_height, plate_thickness)
tab = Pos(0, plate_height/2 + tab_height/2, 0) * Box(tab_width, tab_height, plate_thickness)
result = result + tab

top_face = result.faces().sort_by(Axis.Z)[-1]
result = fillet(top_face.edges(), fillet_radius)

result = result - Cylinder(cutout_diameter/2, plate_thickness * 2)
result = result - Pos(-mount_hole_spacing/2, 0, 0) * Cylinder(mount_hole_diameter/2, plate_thickness * 2)
result = result - Pos(mount_hole_spacing/2, 0, 0) * Cylinder(mount_hole_diameter/2, plate_thickness * 2)

rib = Pos(0, rib_offset_y, -plate_thickness/2 - rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
result = result + rib

part = result
part.name = "plate_with_tab_and_rib"
export_step(part, "output.step")