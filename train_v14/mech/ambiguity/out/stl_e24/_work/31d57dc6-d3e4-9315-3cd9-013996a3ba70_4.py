from build123d import *

tube_length = 80.0
outer_radius = 20.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
vent_length = 30.0
vent_width = 1.5
vent_position = tube_length / 2.0
chamfer_size = 0.5

outer_cyl = Cylinder(outer_radius, tube_length * 2)
inner_cyl = Cylinder(inner_radius, tube_length * 2)
tube = outer_cyl - inner_cyl

vent_box = Pos(outer_radius - wall_thickness / 2.0, 0, 0) * Box(wall_thickness * 2.0, vent_width, vent_length)
vent_edges = vent_box.edges().filter_by(Axis.Z)
vent_box = chamfer(vent_edges, chamfer_size)

tube = tube - vent_box
tube = tube - Rot(0, 0, 180) * vent_box

part = tube
part.name = "tube_with_vents"
export_step(part, "output.step")