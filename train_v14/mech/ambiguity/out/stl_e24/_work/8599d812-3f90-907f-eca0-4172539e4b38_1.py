from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 4.0
pocket_width = 30.0
pocket_depth = 20.0
pocket_cut_depth = 2.0
hole_diameter = 3.0
hole_offset = 5.0
fillet_radius = 0.5

solid = Box(plate_width, plate_depth, plate_thickness)
solid = fillet(solid.edges().filter_by(Axis.Z), fillet_radius)

pocket = Box(pocket_width, pocket_depth, pocket_cut_depth)
solid = solid - pocket

hole_positions = [
    (-plate_width/2 + hole_offset, -plate_depth/2 + hole_offset),
    ( plate_width/2 - hole_offset, -plate_depth/2 + hole_offset),
    ( plate_width/2 - hole_offset,  plate_depth/2 - hole_offset),
    (-plate_width/2 + hole_offset,  plate_depth/2 - hole_offset),
]
for x, y in hole_positions:
    solid = solid - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 1)

part = solid
part.name = "plate_with_pocket_and_holes"
export_step(part, "output.step")