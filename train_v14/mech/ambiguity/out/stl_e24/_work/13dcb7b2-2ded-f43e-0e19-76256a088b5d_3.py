from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rim_height = 3.0
rim_thickness = 4.0
boss_diameter = 12.0
boss_height = 10.0
boss_spacing_x = 30.0
boss_spacing_y = 25.0
hole_diameter = 6.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0
hole_rows = 2
hole_cols = 3
chamfer_dist = 1.0
fillet_radius = 2.0
pocket_depth = 2.0
pocket_margin = 5.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)
    with BuildSketch(Plane.XY.offset(plate_thickness)) as s2:
        Rectangle(plate_length, plate_width)
    with BuildSketch(Plane.XY.offset(plate_thickness + rim_height)) as s3:
        Rectangle(plate_length - 2*rim_thickness, plate_width - 2*rim_thickness)
    loft()

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_dist)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

boss_positions = [
    (-boss_spacing_x/2, -boss_spacing_y/2),
    ( boss_spacing_x/2, -boss_spacing_y/2),
    (-boss_spacing_x/2,  boss_spacing_y/2),
    ( boss_spacing_x/2,  boss_spacing_y/2),
]
for x, y in boss_positions:
    solid_body = solid_body + Pos(x, y, plate_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)

hole_points = []
for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        hole_points.append((x, y))
for x, y in hole_points:
    solid_body = solid_body - Pos(x, y, plate_thickness + boss_height/2) * Cylinder(hole_diameter/2, plate_thickness + boss_height + 10)

pocket_w = plate_length - 2 * pocket_margin
pocket_h = plate_width - 2 * pocket_margin
solid_body = solid_body - Pos(0, 0, pocket_depth/2) * Box(pocket_w, pocket_h, pocket_depth)

part = solid_body
part.name = "plate_with_rim_bosses_holes_pocket"
export_step(part, "output.step")