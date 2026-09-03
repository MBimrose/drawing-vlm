from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 5.0
pocket_width = 40.0
pocket_height = 30.0
pocket_depth = 3.0
vent_hole_diameter = 3.0
vent_rows = 4
vent_cols = 6
vent_spacing_x = 8.0
vent_spacing_y = 8.0
mount_hole_diameter = 5.0
mount_hole_offset = 8.0
chamfer_size = 1.0
rib_thickness = 2.0
rib_height = 2.0
rib_spacing = 20.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_height)
    extrude(amount=plate_thickness)

solid_body = p.part

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

pocket = Pos(0, 0, plate_thickness - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket

for i in range(vent_cols):
    for j in range(vent_rows):
        x = (i - (vent_cols - 1) / 2) * vent_spacing_x
        y = (j - (vent_rows - 1) / 2) * vent_spacing_y
        solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(vent_hole_diameter/2, plate_thickness + 1)

corner_positions = [
    (-plate_width/2 + mount_hole_offset, -plate_height/2 + mount_hole_offset),
    ( plate_width/2 - mount_hole_offset, -plate_height/2 + mount_hole_offset),
    (-plate_width/2 + mount_hole_offset,  plate_height/2 - mount_hole_offset),
    ( plate_width/2 - mount_hole_offset,  plate_height/2 - mount_hole_offset),
]
for x, y in corner_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_diameter/2, plate_thickness + 1)

rib1 = Pos(-rib_spacing/2, 0, plate_thickness - rib_height/2) * Box(rib_thickness, plate_height - 2*mount_hole_offset, rib_height)
rib2 = Pos(rib_spacing/2, 0, plate_thickness - rib_height/2) * Box(rib_thickness, plate_height - 2*mount_hole_offset, rib_height)
solid_body = solid_body + rib1 + rib2

part = solid_body
part.name = "ventilated_plate_with_ribs"
export_step(part, "output.step")