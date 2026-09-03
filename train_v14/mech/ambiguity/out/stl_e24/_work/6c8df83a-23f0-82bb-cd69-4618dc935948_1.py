from build123d import *

length = 80.0
width = 50.0
height = 30.0
wall_thickness = 3.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 10.0
hole_diameter = 4.0
hole_spacing = 20.0
hole_rows = 3
hole_columns = 3
fillet_radius = 0.2
rib_thickness = 2.0
rib_height = 5.0

base = Pos(0, 0, height/2) * Box(length, width, height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

rib = Pos(0, 0, wall_thickness + rib_height/2) * Box(length - 2*wall_thickness, rib_thickness, rib_height)
base = base + rib

pocket = Pos(0, 0, height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
base = base - pocket

hole_r = hole_diameter / 2
hole_h = width + 10
for i in range(hole_columns):
    for j in range(hole_rows):
        x = (i - (hole_columns-1)/2) * hole_spacing
        z = (j - (hole_rows-1)/2) * hole_spacing + height/2
        base = base - Pos(x, width/2, z) * Rot(90, 0, 0) * Cylinder(hole_r, hole_h)
        base = base - Pos(x, -width/2, z) * Rot(90, 0, 0) * Cylinder(hole_r, hole_h)

base = fillet(base.edges(), fillet_radius)

part = base
part.name = "shelled_box_with_rib_pocket_holes"
export_step(part, "output.step")