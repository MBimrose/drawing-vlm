from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
pocket_length = 50.0
pocket_width = 30.0
pocket_depth = 3.0
hole_diameter = 7.0
hole_spacing = 30.0
hole_offset_y = 20.0
chamfer_size = 0.5
rib_thickness = 4.0
rib_height = 2.0
rib_offset = 5.0

base = Box(plate_length, plate_width, plate_thickness)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
base = base - pocket

for x, y in [(-hole_spacing, 0), (0, hole_offset_y), (hole_spacing, 0)]:
    base = base - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

top_face = base.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
base = chamfer(top_edges, chamfer_size)

rib = Pos(0, 0, rib_height/2) * Box(rib_thickness, plate_width - 2*rib_offset, rib_height)
base = base + rib

part = base
part.name = "plate_with_pocket_holes_and_rib"
export_step(part, "output.step")