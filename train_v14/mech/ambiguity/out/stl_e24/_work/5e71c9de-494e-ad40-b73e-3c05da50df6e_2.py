from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
edge_fillet_radius = 3.0
pocket_diameter = 30.0
pocket_depth = 6.0
hole_diameter = 8.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
boss_diameter = 20.0
boss_height = 4.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), edge_fillet_radius)

solid_body = solid_body - Pos(0, 0, plate_thickness) * Cylinder(pocket_diameter/2, pocket_depth)

hole_positions = [
    (-hole_spacing_x/2, -hole_spacing_y/2),
    ( hole_spacing_x/2, -hole_spacing_y/2),
    (-hole_spacing_x/2,  hole_spacing_y/2),
    ( hole_spacing_x/2,  hole_spacing_y/2),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

solid_body = solid_body + Pos(0, 0, boss_height/2) * Cylinder(boss_diameter/2, boss_height)

part = solid_body
part.name = "plate_with_pocket_holes_and_boss"
export_step(part, "output.step")