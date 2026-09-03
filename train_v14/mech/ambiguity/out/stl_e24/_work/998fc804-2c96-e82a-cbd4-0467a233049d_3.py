from build123d import *

outer_width = 90.0
outer_height = 60.0
outer_depth = 20.0
wall_thickness = 2.0
base_thickness = 4.0
connector_cutout_width = 30.0
connector_cutout_height = 8.0
connector_cutout_depth = 6.0
hole_diameter = 6.0
hole_margin = 8.0
hole_spacing = (outer_height - 2 * hole_margin) / (5 - 1)
chamfer_size = 0.5

solid_body = Box(outer_width, outer_height, outer_depth)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

base_plate = Pos(0, 0, -outer_depth/2 + base_thickness/2) * Box(outer_width - 2*wall_thickness, outer_height - 2*wall_thickness, base_thickness)
solid_body = solid_body + base_plate

cutout = Pos(0, outer_height/2 - wall_thickness - connector_cutout_depth/2, outer_depth/2) * Box(connector_cutout_width, connector_cutout_depth, connector_cutout_height)
solid_body = solid_body - cutout

for i in range(5):
    y = -outer_height/2 + hole_margin + i * hole_spacing
    hole = Pos(-outer_width/2 + hole_margin, y, 0) * Cylinder(hole_diameter/2, outer_depth)
    solid_body = solid_body - hole

top_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "hollow_box_with_cutouts"
export_step(part, "output.step")