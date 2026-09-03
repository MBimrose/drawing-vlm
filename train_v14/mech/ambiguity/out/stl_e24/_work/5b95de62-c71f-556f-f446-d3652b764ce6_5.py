from build123d import *

plate_width = 80.0
plate_height = 80.0
plate_thickness = 10.0
cutout_size = 40.0
rib_width = 10.0
rib_height = 5.0
hole_diameter = 5.0
hole_spacing = 25.0
chamfer_distance = 0.5

base = Box(plate_width, plate_height, plate_thickness)
cutout = Box(cutout_size, cutout_size, plate_thickness + 1)
base = base - cutout

rib = Box(rib_width, rib_width, rib_height)
rib_positions = [
    (plate_width/2 - rib_width/2, plate_height/2 - rib_width/2),
    (-plate_width/2 + rib_width/2, plate_height/2 - rib_width/2),
    (plate_width/2 - rib_width/2, -plate_height/2 + rib_width/2),
    (-plate_width/2 + rib_width/2, -plate_height/2 + rib_width/2),
]
for x, y in rib_positions:
    base = base + Pos(x, y, 0) * rib

hole = Cylinder(hole_diameter/2, plate_thickness + 1)
for i in range(3):
    for j in range(3):
        x = (i - 1) * hole_spacing
        y = (j - 1) * hole_spacing
        base = base - Pos(x, y, 0) * hole

base = chamfer(base.edges().filter_by(Axis.Z), chamfer_distance)

part = base
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")