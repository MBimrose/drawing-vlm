from build123d import *

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 10.0
rib_height = 2.0
rib_width = 2.0
rib_spacing = 6.0
rib_count = 4
hole_diameter = 10.0
hole_center_x = 0.0
hole_center_y = 0.0
chamfer_distance = 0.3
reinforcement_rib_width = 4.0
reinforcement_rib_length = 20.0
reinforcement_rib_thickness = 2.0

solid_body = Box(jaw_length, jaw_width, jaw_thickness)

for i in range(rib_count):
    y_pos = -jaw_width/2 + rib_spacing + i * rib_spacing
    rib = Pos(0, y_pos, jaw_thickness/2 + rib_height/2) * Box(rib_width, rib_height, rib_height)
    solid_body = solid_body + rib

reinforcement = Pos(-jaw_length/4, 0, -jaw_thickness/2 - reinforcement_rib_length/2) * Box(reinforcement_rib_width, reinforcement_rib_thickness, reinforcement_rib_length)
solid_body = solid_body + reinforcement

hole = Pos(hole_center_x, hole_center_y, 0) * Cylinder(hole_diameter/2, jaw_thickness + rib_height + 10)
solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
rib_edges = [e for e in vertical_edges if e.center().Z > jaw_thickness/2]
solid_body = chamfer(rib_edges, chamfer_distance)

part = solid_body
part.name = "jaw_with_ribs"
export_step(part, "output.step")