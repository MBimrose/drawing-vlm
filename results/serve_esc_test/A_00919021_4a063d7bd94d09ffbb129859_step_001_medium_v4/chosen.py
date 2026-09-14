from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 5.0
rib_height = 12.0
rib_width = 5.0
fillet_radius = 0.4
hole_diameter = 4.0
hole_spacing = 20.0
hole_offset_from_edge = 10.0

base = Box(plate_length, plate_width, plate_thickness)
rib = Pos(0, plate_width/2 - rib_width/2, plate_thickness/2 + rib_height/2) * Box(plate_length, rib_width, rib_height)
solid_body = base + rib

rear_face = solid_body.faces().sort_by(Axis.Y)[-1]
solid_body = fillet(rear_face.edges(), fillet_radius)

hole_r = hole_diameter / 2
hole_h = plate_length + 10
for x in [-plate_length/2 + hole_offset_from_edge, plate_length/2 - hole_offset_from_edge]:
    for z in [plate_thickness/2 + rib_height/2 - hole_spacing/2, plate_thickness/2 + rib_height/2 + hole_spacing/2]:
        solid_body = solid_body - Pos(x, plate_width/2, z) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)

part = solid_body
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")