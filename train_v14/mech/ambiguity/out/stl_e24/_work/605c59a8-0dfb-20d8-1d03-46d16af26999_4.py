from build123d import *

plate_length = 100.0
plate_width = 60.0
plate_thickness = 8.0
rib_height = 30.0
rib_base_width = 20.0
rib_top_width = 12.0
rib_length = 80.0
draft_angle = 5.0
hole_diameter = 5.0
hole_edge_margin = 10.0
chamfer_distance = 0.5

base = Box(plate_length, plate_width, plate_thickness)

with BuildPart() as rib_bp:
    with BuildSketch(Plane.XY.offset(plate_thickness/2)) as sk:
        Rectangle(rib_length, rib_base_width)
    extrude(amount=rib_height, taper=draft_angle)

result = base + rib_bp.part

hole_positions = [
    (-plate_length/2 + hole_edge_margin, -plate_width/2 + hole_edge_margin),
    ( plate_length/2 - hole_edge_margin, -plate_width/2 + hole_edge_margin),
    (-plate_length/2 + hole_edge_margin,  plate_width/2 - hole_edge_margin),
    ( plate_length/2 - hole_edge_margin,  plate_width/2 - hole_edge_margin)
]

for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + rib_height + 20)

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_distance)

part = result
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")