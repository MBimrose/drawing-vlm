from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
edge_chamfer = 2.0
boss_diameter = 12.0
boss_height = 8.0
boss_spacing_x = 30.0
boss_spacing_y = 30.0
boss_rows = 2
boss_cols = 2
hole_diameter = 6.0
pocket_margin = 5.0
pocket_depth = 2.0
fillet_radius = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)
solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), edge_chamfer)

pocket_w = plate_length - 2 * pocket_margin
pocket_h = plate_width - 2 * pocket_margin
pocket_box = Pos(0, 0, plate_thickness - pocket_depth/2) * Box(pocket_w, pocket_h, pocket_depth)
solid_body = solid_body - pocket_box

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

boss_radius = boss_diameter / 2
boss_cyl = Cylinder(boss_radius, boss_height)
hole_cyl = Cylinder(hole_diameter / 2, boss_height + plate_thickness + 10)

x_start = -(boss_spacing_x * (boss_cols - 1) / 2)
y_start = -(boss_spacing_y * (boss_rows - 1) / 2)
for i in range(boss_cols):
    for j in range(boss_rows):
        x = x_start + i * boss_spacing_x
        y = y_start + j * boss_spacing_y
        solid_body = solid_body + Pos(x, y, plate_thickness + boss_height/2) * boss_cyl
        solid_body = solid_body - Pos(x, y, plate_thickness + boss_height/2) * hole_cyl

part = solid_body
part.name = "plate_with_bosses"
export_step(part, "output.step")