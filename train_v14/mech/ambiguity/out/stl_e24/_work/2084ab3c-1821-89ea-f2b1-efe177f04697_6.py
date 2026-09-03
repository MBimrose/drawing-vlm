from build123d import *

panel_width = 80.0
panel_height = 60.0
panel_thickness = 3.0
corner_fillet_radius = 1.5
hole_diameter = 3.2
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 3
notch_width = 12.0
notch_height = 8.0
rib_thickness = 2.0
rib_height = 1.5
boss_diameter = 6.0
boss_height = 2.0

solid_body = Box(panel_width, panel_height, panel_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)

notch = Pos(0, panel_height/2 - notch_height/2, 0) * Box(notch_width, notch_height, panel_thickness)
solid_body = solid_body - notch

rib = Pos(0, 0, panel_thickness/2 + rib_height/2) * Box(rib_thickness, panel_width - 2*corner_fillet_radius, rib_height)
solid_body = solid_body + rib

boss = Pos(0, 0, panel_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        hole = Pos(x, y, 0) * Cylinder(hole_diameter/2, panel_thickness + 10)
        solid_body = solid_body - hole

part = solid_body
part.name = "panel_with_rib_boss_holes"
export_step(part, "output.step")