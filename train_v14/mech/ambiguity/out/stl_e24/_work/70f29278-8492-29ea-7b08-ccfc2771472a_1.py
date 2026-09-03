from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
slot_length = 60.0
slot_width = 8.0
boss_diameter = 12.0
boss_height = 6.0
boss_offset_x = 30.0
hole_diameter = 3.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0
hole_rows = 2
hole_cols = 3
fillet_radius = 2.0
chamfer_distance = 0.5
rib_width = 6.0
rib_length = 48.0
rib_height = 4.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 4.0
pocket_offset_x = -10.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part

with BuildPart() as sp:
    with BuildSketch() as ss:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness + 0.01)
solid_body = solid_body - sp.part

boss = Pos(boss_offset_x, 0, plate_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 0.01)

rib = Pos(0, 0, -rib_height/2) * Box(rib_width, rib_length, rib_height)
solid_body = solid_body + rib

pocket = Pos(pocket_offset_x, 0, pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

part = solid_body
part.name = "plate_with_features"
export_step(part, "output.step")