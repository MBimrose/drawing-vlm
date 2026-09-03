from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 5.0
boss_diameter = 20.0
boss_height = 10.0
hole_diameter = 4.0
hole_spacing_x = 15.0
hole_spacing_y = 12.0
hole_rows = 2
hole_cols = 4
edge_fillet_radius = 1.5
bottom_chamfer = 0.5
rib_width = 5.0
rib_height = 2.0
rib_offset = 5.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), edge_fillet_radius)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), bottom_chamfer)

boss = Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

rib_y = -plate_width/2 + rib_offset + rib_width/2
rib = Pos(0, rib_y, -plate_thickness/2 - rib_height/2) * Box(plate_length - 2*rib_offset, rib_width, rib_height)
solid_body = solid_body + rib

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, y, 0) * Cylinder(hole_diameter/2, 100)
        solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_boss_rib_holes"
export_step(part, "output.step")