from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 6.0
height = 55.0
rib_count = 12
rib_thickness = 2.0
rib_depth = 12.0
rib_height = 45.0
top_chamfer = 1.5

outer_radius = 0.5 * outer_diameter
inner_radius = outer_radius - wall_thickness

result = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), top_chamfer)

rib_array_radius = inner_radius - rib_thickness
for i in range(rib_count):
    angle_deg = i * 360.0 / rib_count
    angle_rad = math.radians(angle_deg)
    px = rib_array_radius * math.cos(angle_rad)
    py = rib_array_radius * math.sin(angle_rad)
    rib = Pos(px, py, 0) * Rot(0, 0, angle_deg) * Pos(rib_thickness/2, 0, rib_height/2) * Box(rib_thickness, rib_depth, rib_height)
    result = result + rib

part = result
part.name = "XMountSocket"
export_step(part, OUTPUT_PATH)