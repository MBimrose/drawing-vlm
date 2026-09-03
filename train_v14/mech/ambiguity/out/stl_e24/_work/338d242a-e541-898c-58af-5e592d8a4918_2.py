from build123d import *

tube_length = 80.0
outer_radius = 12.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
keyway_width = 4.0
keyway_depth = wall_thickness - 0.5
keyway_length = 20.0
hole_diameter = 2.0
hole_spacing = 6.0
hole_count = int((tube_length - 20) // hole_spacing)

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, tube_length))
            l3 = Line(l2@1, (inner_radius, tube_length))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

keyway_box = Pos(outer_radius - keyway_depth/2, 0, tube_length/2 - keyway_length/2) * Box(keyway_depth, keyway_width, keyway_length)
solid_body = solid_body - keyway_box

for i in range(hole_count):
    z_pos = tube_length/2 + (i - (hole_count-1)/2) * hole_spacing
    hole = Pos(outer_radius - wall_thickness/2, 0, z_pos) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, wall_thickness)
    solid_body = solid_body - hole

part = solid_body
part.name = "tube_with_keyway_and_holes"
export_step(part, "output.step")