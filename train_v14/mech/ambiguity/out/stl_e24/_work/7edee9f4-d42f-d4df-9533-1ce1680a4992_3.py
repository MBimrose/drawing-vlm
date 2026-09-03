from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 6.0
boss_radius = 8.0
boss_height = 12.0
hole_diameter = 3.2
hole_spacing_x = 40.0
hole_spacing_y = 30.0
chamfer_size = 1.0
rib_width = 10.0
rib_height = 4.0
rib_thickness = 2.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_width, plate_depth, plate_thickness)
boss = Pos(0, 0, plate_thickness) * Cylinder(boss_radius, boss_height)
rib = Pos(-plate_width/2 + rib_width/2, 0, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)

solid = base + boss + rib

hole_positions = [
    (hole_spacing_x/2, hole_spacing_y/2),
    (hole_spacing_x/2, -hole_spacing_y/2),
    (-hole_spacing_x/2, hole_spacing_y/2),
    (-hole_spacing_x/2, -hole_spacing_y/2),
]

for x, y in hole_positions:
    solid = solid - Pos(x, y, plate_thickness + boss_height/2) * Cylinder(hole_diameter/2, 30)

top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = chamfer(top_face.edges(), chamfer_size)

part = solid
part.name = "plate_with_boss_and_rib"
export_step(part, "output.step")