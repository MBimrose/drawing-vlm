from build123d import *

plate_width = 70.0
plate_height = 50.0
plate_thickness = 4.0
tab_width = 20.0
tab_height = 10.0
pocket_width = 30.0
pocket_height = 20.0
slot_width = 5.0
slot_length = 60.0
slot_offset_y = -plate_height/2 + 10.0
hole_diameter = 5.5
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 3
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(
                (-plate_width/2, -plate_height/2),
                (plate_width/2, -plate_height/2),
                (plate_width/2, plate_height/2),
                (plate_width/2 + tab_width, plate_height/2),
                (plate_width/2 + tab_width, plate_height/2 + tab_height),
                (plate_width/2, plate_height/2 + tab_height),
                (-plate_width/2, plate_height/2 + tab_height),
                close=True
            )
        make_face()
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, plate_thickness/2) * Box(pocket_width, pocket_height, plate_thickness)
solid_body = solid_body - Pos(0, slot_offset_y, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = hole_spacing_x/2 + i * hole_spacing_x
        y = hole_spacing_y/2 + j * hole_spacing_y
        solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_tab_pocket_slot_holes"
export_step(part, "output.step")