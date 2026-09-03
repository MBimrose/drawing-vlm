from build123d import *

plate_width = 80.0
plate_height = 50.0
plate_thickness = 3.0
edge_fillet_radius = 1.5
hole_diameter = 3.2
hole_spacing_x = 20.0
hole_spacing_y = 15.0
hole_rows = 2
hole_cols = 3
slot_width = 12.0
slot_length = 20.0
rib_height = 1.0
rib_width = 2.0
boss_diameter = 6.0
boss_height = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_height)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), edge_fillet_radius)

rib = Pos(0, 0, plate_thickness + rib_height/2) * Box(rib_width, plate_width - 2 * edge_fillet_radius, rib_height)
solid_body = solid_body + rib

boss = Pos(0, 0, plate_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        hole = Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 1)
        solid_body = solid_body - hole

slot = Pos(0, plate_height/2 - plate_thickness/2, plate_thickness/2) * Box(slot_width, plate_thickness, slot_length)
solid_body = solid_body - slot

part = solid_body
part.name = "plate_with_rib_boss_holes_slot"
export_step(part, "output.step")