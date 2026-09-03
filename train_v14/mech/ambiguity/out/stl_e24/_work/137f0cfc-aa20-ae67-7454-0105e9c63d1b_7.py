from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 5.0
tab_width = 20.0
tab_height = 15.0
central_hole_diameter = 30.0
mounting_hole_diameter = 10.0
mounting_hole_spacing = 30.0
notch_radius = 8.0
fillet_radius = 1.0
rib_width = 10.0
rib_height = 20.0
rib_thickness = 2.0
rib_offset_y = -plate_height / 4

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_height)
    extrude(amount=plate_thickness)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = fillet(top_edges, fillet_radius)

tab = Pos(0, plate_height/2 + tab_height/2, plate_thickness/2) * Box(tab_width, tab_height, plate_thickness)
solid_body = solid_body + tab

solid_body = solid_body - Pos(0, 0, plate_thickness/2) * Cylinder(central_hole_diameter/2, plate_thickness + 1)

for x in [-mounting_hole_spacing/2, mounting_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, plate_thickness/2) * Cylinder(mounting_hole_diameter/2, plate_thickness + 1)

notch = Pos(0, -plate_height/2 + notch_radius, plate_thickness/2) * Cylinder(notch_radius, plate_thickness + 1)
solid_body = solid_body - notch

rib = Pos(0, rib_offset_y, -rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_tab_and_rib"
export_step(part, "output.step")