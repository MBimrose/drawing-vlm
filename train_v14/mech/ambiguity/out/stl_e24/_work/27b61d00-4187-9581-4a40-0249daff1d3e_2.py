from build123d import *

outer_diameter = 80.0
height = 60.0
wall_thickness = 6.0
rib_height = 30.0
rib_width = 12.0
rib_thickness = 2.0
rib_count = 12
central_bore_diameter = 20.0
chamfer_distance = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness
rib_center_radius = inner_radius - rib_thickness / 2.0

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)
solid_body = solid_body - Cylinder(central_bore_diameter / 2, height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(rib_center_radius, 0, height / 2) * Box(rib_thickness, rib_width, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")