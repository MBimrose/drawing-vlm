from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 6.0
height = 50.0
rib_count = 8
rib_width = 4.0
rib_height = 12.0
rib_depth = 3.0
groove_width = 4.0
groove_depth = 2.0
groove_position = 30.0
chamfer_size = 1.0
hole_diameter = 5.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

solid_body = solid_body - Cylinder(hole_diameter / 2, height)

groove_radius = inner_radius - groove_depth
groove_z = height - groove_position - groove_width / 2.0
solid_body = solid_body - Pos(0, 0, groove_z) * Cylinder(groove_radius, groove_width)

rib_center_radius = inner_radius - rib_depth / 2.0
for i in range(rib_count):
    angle = math.radians(i * 360.0 / rib_count)
    px = rib_center_radius * math.cos(angle)
    py = rib_center_radius * math.sin(angle)
    rib = Pos(px, py, height / 2.0) * Box(rib_depth, rib_height, height)
    solid_body = solid_body + rib

part = solid_body
part.name = "ribbed_cylinder_with_groove"
export_step(part, "output.step")