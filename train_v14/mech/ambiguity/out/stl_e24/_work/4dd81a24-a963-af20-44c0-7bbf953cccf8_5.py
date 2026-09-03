from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 5.0
chamfer_distance = 2.0
pocket_length = 60.0
pocket_width = 40.0
pocket_depth = 3.0
hole_diameter = 4.5
hole_spacing_x = 30.0
hole_spacing_y = 30.0
hole_rows = 2
hole_cols = 2
rib_thickness = 2.0
rib_height = 4.0
rib_offset = 5.0

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_distance)

pocket = Pos(0, 0, plate_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
base = base - pocket

rib_y = -(plate_width/2 - rib_offset - rib_thickness/2)
rib = Pos(0, rib_y, plate_thickness + rib_height/2) * Box(plate_length - 2*rib_offset, rib_thickness, rib_height)
base = base + rib

hole_r = hole_diameter / 2
hole_h = plate_thickness + rib_height + 10
for i in range(hole_cols):
    for j in range(hole_rows):
        x = -plate_length/2 + hole_spacing_x/2 + i*hole_spacing_x
        y = -plate_width/2 + hole_spacing_y/2 + j*hole_spacing_y
        base = base - Pos(x, y, plate_thickness/2) * Cylinder(hole_r, hole_h)

part = base
part.name = "plate_with_pocket_rib_holes"
export_step(part, "output.step")