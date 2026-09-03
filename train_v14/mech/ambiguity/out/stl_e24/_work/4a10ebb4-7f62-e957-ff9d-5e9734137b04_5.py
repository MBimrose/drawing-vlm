from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
base_plate_thickness = 4.0
rib_height = 5.0
rib_thickness = 2.0

outer_box = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
inner_box = Pos(0, 0, outer_height/2) * Box(outer_length - 2*wall_thickness, outer_width - 2*wall_thickness, outer_height - 2*wall_thickness)
enclosure = outer_box - inner_box

base_plate = Pos(0, 0, -base_plate_thickness/2) * Box(outer_length - 2*wall_thickness, outer_width - 2*wall_thickness, base_plate_thickness)
enclosure = enclosure + base_plate

rib = Pos(0, 0, -base_plate_thickness - rib_height/2) * Box(outer_length - 2*wall_thickness, rib_thickness, rib_height)
enclosure = enclosure + rib

part = enclosure
part.name = "enclosure_with_base_plate_and_rib"
export_step(part, "output.step")