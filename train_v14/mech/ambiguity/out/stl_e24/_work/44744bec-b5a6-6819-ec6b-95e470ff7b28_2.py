from build123d import *

plate_width = 70.0
plate_depth = 30.0
plate_thickness = 5.0
pocket_width = 30.0
pocket_depth = 15.0
pocket_cut_depth = 2.0
hole_diameter = 3.0
countersink_diameter = 5.0
countersink_angle = 82.0
hole_spacing = 20.0
chamfer_size = 0.5
rib_height = 2.0
rib_thickness = 4.0
rib_offset = 5.0

solid = Box(plate_width, plate_depth, plate_thickness)

pocket = Pos(0, 0, plate_thickness/2 - pocket_cut_depth/2) * Box(pocket_width, pocket_depth, pocket_cut_depth)
solid = solid - pocket

rib = Pos(0, 0, -plate_thickness/2 + rib_height/2) * Box(plate_width - 2*rib_offset, rib_thickness, rib_height)
solid = solid + rib

hole_positions = [(-hole_spacing, 0), (0, 0), (hole_spacing, 0)]
for x, y in hole_positions:
    csk = Pos(x, y, plate_thickness/2) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, plate_thickness, countersink_angle)
    solid = solid - csk

vertical_edges = solid.edges().filter_by(Axis.Z)
solid = chamfer(vertical_edges, chamfer_size)

part = solid
part.name = "plate_with_pocket_rib_holes"
export_step(part, "output.step")