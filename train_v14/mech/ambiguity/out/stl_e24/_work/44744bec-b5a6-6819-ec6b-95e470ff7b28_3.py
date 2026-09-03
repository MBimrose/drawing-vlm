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

solid_body = Box(plate_width, plate_depth, plate_thickness)

pocket = Pos(0, 0, plate_thickness/2 - pocket_cut_depth/2) * Box(pocket_width, pocket_depth, pocket_cut_depth)
solid_body = solid_body - pocket

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

for x in [-hole_spacing, 0, hole_spacing]:
    csk = Pos(x, 0, plate_thickness/2) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, plate_thickness, countersink_angle)
    solid_body = solid_body - csk

part = solid_body
part.name = "plate_with_pocket_and_holes"
export_step(part, "output.step")