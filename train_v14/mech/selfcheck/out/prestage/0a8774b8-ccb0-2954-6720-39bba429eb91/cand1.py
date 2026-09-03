from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
corner_chamfer = 2.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
rib_width = 10.0
rib_height = 4.0
rib_offset = 10.0
vent_hole_diameter = 4.0
vent_rows = 2
vent_cols = 3
vent_spacing_x = 12.0
vent_spacing_y = 12.0
vent_offset_x = 20.0
vent_offset_y = 10.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)
solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), corner_chamfer)

mount_points = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (-plate_length/2 + mount_hole_offset,  plate_width/2 - mount_hole_offset),
    ( plate_length/2 - mount_hole_offset,  plate_width/2 - mount_hole_offset)
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_diameter/2, plate_thickness)

rib_center_y = -plate_width/2 + rib_offset + rib_width/2
rib = Pos(0, rib_center_y, rib_height/2) * Box(plate_length - 2*rib_offset, rib_width, rib_height)
solid_body = solid_body + rib

vent_points = []
for i in range(vent_cols):
    for j in range(vent_rows):
        x = vent_offset_x + (i - (vent_cols-1)/2) * vent_spacing_x
        y = vent_offset_y + (j - (vent_rows-1)/2) * vent_spacing_y
        vent_points.append((x, y))
for x, y in vent_points:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(vent_hole_diameter/2, plate_thickness)

part = solid_body
part.name = "plate_with_ribs_and_vents"
export_step(part, "output.step")