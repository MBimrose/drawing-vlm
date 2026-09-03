from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
gusset_length = 20.0
gusset_width = 15.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 4.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 3
chamfer_size = 0.5
rib_thickness = 3.0
rib_height = 6.0
rib_spacing = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(
                (-plate_length/2, -plate_width/2),
                (plate_length/2, -plate_width/2),
                (plate_length/2, -plate_width/2 + gusset_width/2),
                (plate_length/2 + gusset_length, -plate_width/2 + gusset_width/2),
                (plate_length/2, -plate_width/2 + gusset_width),
                (plate_length/2, plate_width/2),
                (-plate_length/2, plate_width/2),
                close=True
            )
        make_face()
    extrude(amount=plate_thickness)

solid_body = p.part

pocket = Pos(0, 0, -plate_thickness/2 + pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

rib1 = Pos(0, -rib_spacing/2, plate_thickness/4) * Box(rib_thickness, rib_height, plate_thickness/2)
rib2 = Pos(0, rib_spacing/2, plate_thickness/4) * Box(rib_thickness, rib_height, plate_thickness/2)
solid_body = solid_body + rib1 + rib2

part = solid_body
part.name = "plate_with_gusset_pocket_holes_ribs"
export_step(part, "output.step")