from build123d import *
import math

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 5.0
pocket_width = 40.0
pocket_depth = 30.0
pocket_height = 2.5
hole_diameter = 4.0
hole_spacing = 30.0
countersink_angle = 82.0
chamfer_size = 1.0
rib_width = 10.0
rib_depth = 5.0
rib_height = 2.0
rib_offset_y = 15.0

solid = Box(plate_width, plate_depth, plate_thickness)

pocket = Pos(0, plate_depth/2 - pocket_depth/2, plate_thickness/2 - pocket_height/2) * Box(pocket_width, pocket_height, pocket_height)
solid = solid - pocket

csk_radius = hole_diameter/2 + plate_thickness * math.tan(math.radians(countersink_angle/2))
for x in [-hole_spacing/2, hole_spacing/2]:
    csk = Pos(x, 0, plate_thickness/2) * CounterSinkHole(hole_diameter/2, csk_radius, plate_thickness, countersink_angle)
    solid = solid - csk

rib = Pos(0, -plate_depth/2 + rib_offset_y, -plate_thickness/2 + rib_height/2) * Box(rib_width, rib_depth, rib_height)
solid = solid + rib

rear_face = solid.faces().sort_by(Axis.Y)[0]
rear_edges = rear_face.edges()
solid = chamfer(rear_edges, chamfer_size)

part = solid
part.name = "plate_with_pocket_holes_rib"
export_step(part, "output.step")