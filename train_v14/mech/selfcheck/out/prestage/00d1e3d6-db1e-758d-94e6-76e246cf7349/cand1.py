from build123d import *

plate_width = 80.0
plate_depth = 80.0
plate_thickness = 6.0
boss_radius = 15.0
boss_height = 4.0
rib_width = 10.0
rib_height = 4.0
rib_offset = 5.0
hole_diameter = 5.0
cbore_diameter = 8.0
cbore_depth = 2.0
hole_spacing = 12.0
hole_count = 5
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_depth)
    extrude(amount=plate_thickness)
    with BuildSketch() as s2:
        Circle(boss_radius)
    extrude(amount=boss_height)

solid = p.part

rib_positions = [
    (plate_width/2 - rib_offset - rib_width/2, plate_depth/2 - rib_offset - rib_width/2),
    (-plate_width/2 + rib_offset + rib_width/2, plate_depth/2 - rib_offset - rib_width/2),
    (-plate_width/2 + rib_offset + rib_width/2, -plate_depth/2 + rib_offset + rib_width/2),
    (plate_width/2 - rib_offset - rib_width/2, -plate_depth/2 + rib_offset + rib_width/2),
]
for x, y in rib_positions:
    solid = solid + Pos(x, y, rib_height/2) * Box(rib_width, rib_width, rib_height)

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    solid = solid - Pos(x, 0, plate_thickness) * CounterBoreHole(hole_diameter/2, cbore_diameter/2, cbore_depth, plate_thickness + 10)

top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = chamfer(top_face.edges(), chamfer_size)

part = solid
part.name = "plate_with_boss_ribs_and_holes"
export_step(part, "output.step")