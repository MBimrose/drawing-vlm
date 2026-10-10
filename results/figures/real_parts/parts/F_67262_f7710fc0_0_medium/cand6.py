from build123d import *

plate_length = 80.0
plate_width = 32.0
plate_thickness = 8.0
boss_radius = 8.0
boss_height = 24.0
boss_offset = 12.0
hole_diameter = 4.0
hole_spacing = 12.0
hole_rows = 2
hole_cols = 2
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-plate_length/2 + plate_width/2, -plate_width/2), (plate_length/2 - plate_width/2, -plate_width/2))
            a1 = ThreePointArc(l1 @ 1, (plate_length/2, 0), (plate_length/2 - plate_width/2, plate_width/2))
            l2 = Line(a1 @ 1, (-plate_length/2 + plate_width/2, plate_width/2))
            a2 = ThreePointArc(l2 @ 1, (-plate_length/2, 0), (-plate_length/2 + plate_width/2, -plate_width/2))
        make_face()
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

solid_body = solid_body + Pos(-plate_length/2 + boss_offset, 0, plate_thickness + boss_height/2) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + Pos(plate_length/2 - boss_offset, 0, -boss_height/2) * Cylinder(boss_radius, boss_height)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing
        y = (j - (hole_rows - 1) / 2) * hole_spacing
        solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 10)

part = solid_body
part.name = "plate_with_bosses_and_holes"
export_step(part, "output.step")