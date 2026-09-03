from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 12.0
arc_radius = 30.0
pocket_length = plate_length - 10.0
pocket_width = 10.0
pocket_depth = 8.0
hole_diameter = 6.0
hole_offset = 8.0
chamfer_size = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-plate_length/2, -plate_width/2), (plate_length/2, -plate_width/2))
            a1 = ThreePointArc(l1@1, (plate_length/2 + arc_radius/2, 0), (plate_length/2, plate_width/2))
            l2 = Line(a1@1, (-plate_length/2, plate_width/2))
            a2 = ThreePointArc(l2@1, (-plate_length/2 - arc_radius/2, 0), (-plate_length/2, -plate_width/2))
        make_face()
    extrude(amount=plate_thickness)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

pocket = Pos(0, 0, plate_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

hole_positions = [
    (plate_length/2 - hole_offset, plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset, plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    (plate_length/2 - hole_offset, -plate_width/2 + hole_offset)
]

for x, y in hole_positions:
    hole = Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)
    solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_arcs_pocket_and_holes"
export_step(part, "output.step")