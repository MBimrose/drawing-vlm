from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 10.0
central_hole_dia = 20.0
blind_hole_dia = 8.0
blind_hole_depth = 8.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
chamfer_size = 1.0
rib_width = 6.0
rib_height = 4.0
rib_spacing = 20.0
boss_dia = 30.0
boss_height = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
        Circle(central_hole_dia / 2, mode=Mode.SUBTRACT)
    extrude(amount=plate_thickness)

solid_body = p.part

for x, y in [(-hole_spacing_x/2, -hole_spacing_y/2), (hole_spacing_x/2, -hole_spacing_y/2),
             (-hole_spacing_x/2, hole_spacing_y/2), (hole_spacing_x/2, hole_spacing_y/2)]:
    solid_body = solid_body - Pos(x, y, plate_thickness) * Cylinder(blind_hole_dia/2, blind_hole_depth)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

rib1 = Pos(0, -rib_spacing/2, plate_thickness/2) * Box(plate_length - 2*rib_spacing, rib_width, rib_height)
rib2 = Pos(0, rib_spacing/2, plate_thickness/2) * Box(plate_length - 2*rib_spacing, rib_width, rib_height)
solid_body = solid_body + rib1 + rib2

boss = Pos(0, 0, plate_thickness + boss_height/2) * Cylinder(boss_dia/2, boss_height)
solid_body = solid_body + boss

part = solid_body
part.name = "plate_with_ribs_and_boss"
export_step(part, "output.step")