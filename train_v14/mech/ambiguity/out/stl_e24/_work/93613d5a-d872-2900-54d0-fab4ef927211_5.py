from build123d import *

plate_width = 80.0
plate_height = 50.0
plate_thickness = 8.0
spline_offset = 10.0
boss_diameter = 30.0
boss_height = 6.0
hole_diameter = 4.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0
hole_rows = 2
hole_cols = 3
chamfer_size = 1.0
pocket_width = 12.0
pocket_height = 8.0
pocket_depth = 4.0
pocket_offset_x = 30.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-plate_width/2, -plate_height/2), (plate_width/2, -plate_height/2))
            l2 = Line(l1@1, (plate_width/2, plate_height/2))
            l3 = Line(l2@1, (plate_width/2 - spline_offset, plate_height/2))
            s1 = Spline(l3@1, (plate_width/2 - 2*spline_offset, plate_height/2 + 5),
                        (0, plate_height/2 + 10), (-plate_width/2 + 2*spline_offset, plate_height/2 + 5),
                        (-plate_width/2 + spline_offset, plate_height/2))
            l4 = Line(s1@1, (-plate_width/2, -plate_height/2))
        make_face()
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = solid_body + Pos(0, 0, plate_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body - Pos(pocket_offset_x, 0, plate_thickness - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_boss_pockets_and_holes"
export_step(part, "output.step")