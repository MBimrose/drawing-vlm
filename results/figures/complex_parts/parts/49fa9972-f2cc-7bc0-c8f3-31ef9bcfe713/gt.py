from build123d import *

outer_width = 80.0
outer_height = 40.0
thickness = 20.0
corner_radius = 5.0
luminaire_radius = 12.0
cable_slot_width = 10.0
cable_slot_height = 6.0
mount_hole_diameter = 6.0
mount_hole_offset = 8.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            a1 = ThreePointArc((-outer_width/2, -outer_height/2 + corner_radius),
                                (-outer_width/2, -outer_height/2),
                                (-outer_width/2 + corner_radius, -outer_height/2))
            l1 = Line(a1@1, (outer_width/2 - corner_radius, -outer_height/2))
            a2 = ThreePointArc(l1@1, (outer_width/2, -outer_height/2),
                                (outer_width/2, -outer_height/2 + corner_radius))
            l2 = Line(a2@1, (outer_width/2, outer_height/2))
            l3 = Line(l2@1, (-outer_width/2, outer_height/2))
            l4 = Line(l3@1, a1@0)
        make_face()
    extrude(amount=thickness)

solid = p.part

slot = Pos(outer_width/2, 0, thickness/2) * Box(cable_slot_width, cable_slot_height, thickness)
solid = solid - slot

luminaire = Pos(0, 0, -thickness/4) * Cylinder(luminaire_radius, thickness/2)
solid = solid - luminaire

hole_positions = [
    (-outer_width/2 + mount_hole_offset, -outer_height/2 + mount_hole_offset),
    (outer_width/2 - mount_hole_offset, -outer_height/2 + mount_hole_offset),
    (outer_width/2 - mount_hole_offset, outer_height/2 - mount_hole_offset),
    (-outer_width/2 + mount_hole_offset, outer_height/2 - mount_hole_offset),
]
for x, y in hole_positions:
    hole = Pos(x, y, thickness/2) * Cylinder(mount_hole_diameter/2, thickness)
    solid = solid - hole

vertical_edges = solid.edges().filter_by(Axis.Z)
solid = chamfer(vertical_edges, chamfer_distance)

cut_box = Pos(-outer_width/2, 0, thickness/2) * Box(outer_width, outer_height, thickness)
solid = solid - cut_box

part = solid
part.name = "luminaire_housing"
export_step(part, OUTPUT_PATH)