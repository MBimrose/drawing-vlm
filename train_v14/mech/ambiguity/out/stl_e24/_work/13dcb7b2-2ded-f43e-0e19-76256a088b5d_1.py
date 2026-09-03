from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rim_height = 5.0
rim_taper = 3.0
boss_diameter = 12.0
boss_height = 10.0
boss_spacing_x = 30.0
boss_spacing_y = 30.0
hole_diameter = 6.0
hole_spacing_x = 16.0
hole_spacing_y = 16.0
chamfer_size = 1.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_length, plate_width, plate_thickness)

with BuildPart() as rim_bp:
    with BuildSketch() as s1:
        Rectangle(plate_length, plate_width)
    with BuildSketch(Plane.XY.offset(rim_height)) as s2:
        Rectangle(plate_length - 2*rim_taper, plate_width - 2*rim_taper)
    loft()
rim = rim_bp.part

result = base + rim

boss_positions = [
    (-boss_spacing_x/2, -boss_spacing_y/2),
    (boss_spacing_x/2, -boss_spacing_y/2),
    (-boss_spacing_x/2, boss_spacing_y/2),
    (boss_spacing_x/2, boss_spacing_y/2),
]
for x, y in boss_positions:
    result = result + Pos(x, y, plate_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)

hole_positions = [
    (-hole_spacing_x/2, -hole_spacing_y/2),
    (hole_spacing_x/2, -hole_spacing_y/2),
    (-hole_spacing_x/2, hole_spacing_y/2),
    (hole_spacing_x/2, hole_spacing_y/2),
]
for x, y in hole_positions:
    result = result - Pos(x, y, (plate_thickness + boss_height)/2) * Cylinder(hole_diameter/2, plate_thickness + boss_height)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "plate_with_rim_bosses_and_holes"
export_step(part, "output.step")