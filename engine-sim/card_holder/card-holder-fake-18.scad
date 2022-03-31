include <BOSL/constants.scad>
use <BOSL/shapes.scad>
use <BOSL/transforms.scad>
use <lazy.scad>
use <rounded_collar.scad>

difference_fudge = 0.01;
extrusion_fudge = 0.1;
print_layer_height = 0.15;
wall_thickness = 2;
support_board_thickness = (3/16) * 25.4;
acrylic_thickness = 3.25;

$fn = 31;

include_led_collar = true;

printable();

mag_diam = 8 + extrusion_fudge * 2;
mag_thickness = 3;

trigger_mag_diam = 5 + extrusion_fudge * 2;
trigger_mag_thickness = 1.7;
trigger_mag_stack = 2;

frame_xside_width = 12;
frame_yside_width = 14;
mag_frame_offset = 4;

frame_overlap = 2;

// credit card size
//card_width = 54;
//card_height = 81;

// mini-card
card_width = 37;
card_height = 67;
card_thickness = acrylic_thickness;
card_overlap_fillet = 3;

frame_width = card_width + (frame_xside_width - frame_overlap) * 2;
frame_height = card_height+ (frame_yside_width - frame_overlap) * 2;

reed_length = 15;
reed_width = 3.25 + extrusion_fudge * 2;

bend_allowance = 2;
conn_allowance = 4;

reed_cutout_length = reed_length + bend_allowance * 2;

plate_depth = wall_thickness + reed_width;

thru_hole_diam = 1.5;

resistor_diam = 2.5;
resistor_length = 7;
resistor_leg_length = 24;

res_channel_length = conn_allowance * 2 + resistor_length;
thru_hole_offset = thru_hole_diam / 2 + bend_allowance / 2;

wire_diam = 1;

// use support_board_thickness to make the back frame magnets protrude through the support board (needs fixup though)
mag_projection_depth = 0; 

mag_collar_height = mag_projection_depth + mag_thickness;
mag_collar_diam = mag_diam + mag_frame_offset;

strip_width = 12.5;
strip_height = 1.7;
led_width = 5.2;
led_height = 2.1;

spread_width = frame_width - mag_collar_diam;
spread_height = frame_height - mag_collar_diam;
switch_count = 5;

delta_y = (spread_height / (switch_count + 3));

show_card_mounting = false;

led_collar_top_width = 2;
led_collar_base_width = 5;
led_collar_height = led_height + 1;
led_collar_shoulder_height = support_board_thickness + plate_depth + 3;
led_collar_inside = [led_width + 1, frame_height - led_collar_base_width * 2];
led_collar_tight_radius = 1;
led_collar_wide_radius = 1;
collar_qual = 7;
collar_corner_qual = 11;
led_collar_card_offset = 3;
led_collar_extra_back_frame_overlap = 2;
led_collar_strip_length = led_collar_inside.y - 2;

led_wiring_allowance = 5;
led_collar_strip_slice_z = plate_depth / 2 + support_board_thickness / 2;
led_collar_frame_width = led_collar_inside.x + led_collar_base_width * 2 + led_collar_card_offset;

module back_plate()
{
    signal_connector_length = spread_width / 2 - reed_cutout_length;

    back_frame_width = frame_width + (include_led_collar ? led_collar_frame_width : 0);
    back_frame_offset_x = include_led_collar ? -led_collar_frame_width / 2 : 0;

    if(show_card_mounting) {
        color("magenta")
        tz(plate_depth + support_board_thickness)
        zflip()
        front_plate();
        * cuboid([frame_width, frame_height, plate_depth], 
            fillet=mag_collar_diam / 2, edges=EDGES_Z_ALL);

        color("brown")
        tz(support_board_thickness)
        cuboid([frame_width + led_collar_card_offset * 2, frame_height + 5, plate_depth]);
    }

    difference()
    {
        union()
        {
            // Main back plate
            tx(back_frame_offset_x)
            cuboid([back_frame_width, frame_height, plate_depth], 
                fillet=mag_collar_diam / 2, edges=EDGES_Z_ALL);
                
            // Add in the LED collar
            txz(-back_frame_width / 2 - led_collar_card_offset / 2, -plate_depth / 2)
            round_rect_collar(interior_size=led_collar_inside, 
                top_width=led_collar_top_width, base_width=led_collar_base_width, 
                collar_height=led_collar_height, shoulder_height=led_collar_shoulder_height, 
                inner_radius=led_collar_tight_radius, outer_radius=led_collar_wide_radius, 
                shoulder_radius=led_collar_tight_radius,
                corner_qual=collar_corner_qual, profile_qual=collar_qual);

            // Add support for the LED strip    
            txz(-back_frame_width / 2 - led_collar_card_offset / 2, led_collar_strip_slice_z)
            rz(90)
            downcube([led_collar_strip_length, strip_width, led_collar_strip_slice_z - difference_fudge]);
        }

        // Punch out a tray for the LED strip    
        txz(-back_frame_width / 2 - led_collar_card_offset / 2, led_collar_strip_slice_z)
        rz(90)
        color("black")
        downcube([led_collar_strip_length, strip_width, strip_height]);

        // Punch out slots for the LED strip wires
        txz(-back_frame_width / 2 - led_collar_card_offset / 2, led_collar_strip_slice_z - plate_depth * 5)
        yspread(n=2, l=spread_height)
        cuboid([strip_width, led_wiring_allowance, plate_depth * 10]);
    }
}

module printable()
{
    translate([-50, 0, 0])
    bottom_half(z = led_collar_strip_slice_z - difference_fudge)
    left_half(x= -25)
    back_plate();

    translate([-100, 0, 0])
    top_half(z = led_collar_strip_slice_z - difference_fudge)
    back_plate();
}