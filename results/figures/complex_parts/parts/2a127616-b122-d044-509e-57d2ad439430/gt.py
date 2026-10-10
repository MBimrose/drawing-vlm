from build123d import *
import math

outer_diameter = 60.0
housing_length = 80.0
wall_thickness = 5.0
rib_height = 8.0
rib_width = 6.0
rib_angle_spacing = 30.0
thread_diameter = 20.0
thread_length = 30.0
chamfer_size = 1.0

solid = Cylinder(outer_diameter/2, housing_length)
top_face = solid.faces().sort_by(Axis.Z)[-1]
bottom_face = solid.faces().sort_by(Axis.Z)[0]
solid = offset(solid, amount=-wall_thickness, openings=[top_face, bottom_face])

num_ribs = int(360 / rib_angle_spacing)
r = outer_diameter/2 + rib_height/2
for i in range(num_ribs):
    angle = i * rib_angle_spacing
    rib = Box(rib_width, rib_height, housing_length)
    px = r * math.cos(math.radians(angle))
    py = r * math.sin(math.radians(angle))
    rib = Pos(px, py, 0) * Rot(0, 0, angle) * rib
    solid = solid + rib

insert = Cylinder(thread_diameter/2, thread_length)
insert = Pos(0, 0, -housing_length/2 - thread_length/2) * insert
bottom_edges = insert.edges().sort_by(Axis.Z)[:1]
insert = chamfer(bottom_edges, chamfer_size)

solid = solid + insert
part = solid
part.name = "threaded_housing_with_ribs"
export_step(part, OUTPUT_PATH)