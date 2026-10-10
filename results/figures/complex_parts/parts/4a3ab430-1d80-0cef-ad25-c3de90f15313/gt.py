from build123d import *

base_width = 80.0
base_depth = 80.0
base_thickness = 5.0
hex_radius = 30.0
pocket_depth = 15.0
dome_height = 25.0
dome_radius = 20.0
chamfer_size = 2.0
mount_hole_diameter = 5.0
mount_spacing = 60.0
rib_count = 6
rib_thickness = 3.0
rib_height = 12.0

base = Pos(0, 0, base_thickness/2) * Box(base_width, base_depth, base_thickness)

with BuildPart() as hp:
    with BuildSketch() as s:
        RegularPolygon(hex_radius, 6)
    extrude(amount=-pocket_depth)
hex_prism = Pos(0, 0, base_thickness) * hp.part
base = base - hex_prism

with BuildPart() as dome:
    with BuildSketch(Plane.XY.offset(base_thickness - pocket_depth)) as s1:
        RegularPolygon(hex_radius, 6)
    with BuildSketch(Plane.XY.offset(base_thickness - pocket_depth + dome_height)) as s2:
        Circle(dome_radius)
    loft()
dome_part = dome.part

result = base + dome_part

import math
rad = dome_radius - rib_thickness
for i in range(rib_count):
    theta = i * 2 * math.pi / rib_count
    x = rad * math.cos(theta)
    y = rad * math.sin(theta)
    rib = Pos(x, y, rib_height/2) * Cylinder(rib_thickness/2, rib_height)
    result = result + rib

pts = [
    (mount_spacing/2, mount_spacing/2),
    (-mount_spacing/2, mount_spacing/2),
    (-mount_spacing/2, -mount_spacing/2),
    (mount_spacing/2, -mount_spacing/2),
]
for x, y in pts:
    hole = Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, 100)
    result = result - hole

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

part = result
part.name = "DomeHexLoft"
export_step(part, OUTPUT_PATH)