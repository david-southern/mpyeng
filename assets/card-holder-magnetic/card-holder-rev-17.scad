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

laser_cut = false;

show_back_plate = false;
show_front_plate = true;

$fn = 31;

include_led_collar = true;

printable();

mag_diam = 8 + extrusion_fudge * 2;
// The actual mags are only 3mm thick, but let's add 2mm to make the plate cover fit better
extra_mag_thickness = 2;
actual_mag_thickness = 3;
mag_thickness = actual_mag_thickness + extra_mag_thickness;

trigger_mag_diam = 5 + extrusion_fudge * 2;
actual_trigger_mag_thickness = 1.7;
trigger_mag_stack = 2;

trigger_mag_thickness = actual_trigger_mag_thickness * trigger_mag_stack + extra_mag_thickness;

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

front_cover_depth = 1;

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

mini_collar_width = 0.75;
mini_collar_height = 0.8;
mini_collar_shoulder_height = 0.2;

led_wiring_allowance = 5;
led_collar_strip_slice_z = plate_depth / 2 + support_board_thickness / 2;
led_collar_frame_width = led_collar_inside.x + led_collar_base_width * 2 + led_collar_card_offset;

back_frame_width = frame_width + (include_led_collar ? led_collar_frame_width : 0);
back_frame_offset_x = include_led_collar ? -led_collar_frame_width / 2 : 0;

module mag_collar()
{
    difference()
    {
        color("black")
        cyl(h=mag_collar_height + difference_fudge * 2, d=mag_collar_diam);
        
        color("silver")
        translate([0, 0, 
            mag_collar_height / 2 - mag_thickness / 2 + difference_fudge * 2])
            cyl(h=mag_thickness + difference_fudge, d=mag_diam);        
    }
}

module switch_body()
{
    union() {
        cuboid([reed_cutout_length, reed_width, reed_width]);
        translate([reed_cutout_length / 2, 0, 0])
        cyl(h=99, d=thru_hole_diam);
        translate([-reed_cutout_length / 2, 0, 0])
        cyl(h=99, d=thru_hole_diam);
    }
}

resistor_channel_length = resistor_length + conn_allowance * 2;
    
module resistor_body()
{
    union() {
        color("lightblue")
        xcyl(h=resistor_length, d=resistor_diam);
        
        color("silver")
        xcyl(h=resistor_channel_length, d=wire_diam);
    }
}

module led_strip(strip_length)
{
    color("white")
    upcube([strip_length, led_width, led_height]);
    color("black")
    upcube([strip_length, strip_width, strip_height]);
}

module back_plate()
{
    signal_connector_length = spread_width / 2 - reed_cutout_length;

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
            difference()
            {
                // Main back plate
                tx(back_frame_offset_x)
                cuboid([back_frame_width, frame_height, plate_depth], 
                    fillet=mag_collar_diam / 2, edges=EDGES_Z_ALL);
                
                // Punch out holes for the magnet collars
                yspread(n=2, l=spread_height)
                xspread(n=2, l = spread_width)
                translate([0, 0, 
                    plate_depth / 2 
                        - mag_collar_height / 2 + difference_fudge
                ])
                cyl(h=mag_collar_height, d = mag_collar_diam * 0.98);
            }
/*
            // Add in the LED collar
            txz(-back_frame_width / 2 - led_collar_card_offset / 2, -plate_depth / 2)
            difference()
            {
                upcube([led_width + 1 + led_collar_base_width * 2, frame_height, led_collar_height + led_collar_shoulder_height]);
                cuboid([led_width + 1, frame_height - led_collar_base_width * 2, (led_collar_height + led_collar_shoulder_height) * 3]);
            }
*/            

            txz(-back_frame_width / 2 - led_collar_card_offset / 2, -plate_depth / 2)
            round_rect_collar(interior_size=led_collar_inside, 
                top_width=led_collar_top_width, base_width=led_collar_base_width, 
                collar_height=led_collar_height, shoulder_height=led_collar_shoulder_height, 
                inner_radius=led_collar_tight_radius, outer_radius=led_collar_wide_radius, 
                shoulder_radius=led_collar_tight_radius,
                corner_qual=collar_corner_qual, profile_qual=collar_qual);

            // Add in the top-board mini-collar to hide the cutout
            txz(-back_frame_width / 2 - led_collar_card_offset / 2, plate_depth / 2 + support_board_thickness)
            round_rect_collar(interior_size=led_collar_inside, 
                top_width=led_collar_base_width, base_width=led_collar_base_width + mini_collar_width * 2, 
                collar_height=mini_collar_height, shoulder_height=mini_collar_shoulder_height, 
                inner_radius=led_collar_tight_radius, outer_radius=led_collar_tight_radius, 
                shoulder_radius=led_collar_tight_radius,
                corner_qual=collar_corner_qual, profile_qual=collar_qual);

            // Add support for the LED strip    
            txz(-back_frame_width / 2 - led_collar_card_offset / 2, led_collar_strip_slice_z)
            rz(90)
            downcube([led_collar_strip_length, strip_width, led_collar_strip_slice_z - difference_fudge]);
            
            // Add the magnet collars
            yspread(n=2, l=spread_height)
            xspread(n=2, l = spread_width)
            translate([0, 0, 
                plate_depth / 2 - mag_collar_height / 2 
                    + mag_projection_depth])
            mag_collar();
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

        // Punch out the slots for the reed switches, resistors, and wiring
        for (i = [1 : 1 : switch_count]) {
            x_offset = (i % 2) ? 1 : -1;
            
            y_offset = -spread_height / 2 + delta_y * (i + 1);
            
            translate([
                spread_width / 2 * x_offset - reed_cutout_length / 2 * x_offset, 
                y_offset, 
                plate_depth / 2 - reed_width / 2 + difference_fudge
            ])
            switch_body();
            
            translate([
                spread_width / 2 * x_offset - resistor_channel_length / 2 * x_offset, 
                y_offset, 
                -plate_depth / 2 
            ])
            resistor_body();
            
            // Wiring channel to connect the resistor to the reed switch leg
            color("silver")
            translate([
                signal_connector_length / 2 * x_offset, 
                y_offset, 
                -plate_depth / 2 
            ])
            xcyl(h = signal_connector_length, d=wire_diam);
        }
        
        signal_line_length = frame_height + difference_fudge * 2;
        
        // Wire channel for the analog signal wire and groun wire
        color("silver")
        translate([0, 0, -plate_depth / 2])
        ycyl(h = signal_line_length, d=wire_diam);
        
        // Voltage dividor resistor (470 ohm) channel
        voltage_divider_offset = frame_height / 2 - delta_y;
        translate([
            0, 
            voltage_divider_offset,
            -plate_depth / 2 
        ])
        rotate([0, 0, 90])
        resistor_body();
        
        long_power_line_length = frame_height - delta_y * 2 + difference_fudge * 2;
        long_power_line_offset = delta_y * 1.5 - difference_fudge;
        
        // Wire channel for the incoming +5V to the resistor bases
        color("red")
        translate([
            spread_width / 2 - resistor_channel_length, 
            -long_power_line_offset,
            -plate_depth / 2])
        ycyl(h = long_power_line_length, d=wire_diam);
        
        short_line_length = frame_height - delta_y * 3 + difference_fudge * 2;
        short_line_offset = delta_y * 2 - difference_fudge;

        color("red")
        translate([
            -spread_width / 2 + resistor_channel_length, 
            -short_line_offset, -plate_depth / 2])
        ycyl(h = short_line_length, d=wire_diam);
    }
}

module front_plate()
{
    spread_width = frame_width - mag_collar_diam;
    spread_height = frame_height - mag_collar_diam;
    switch_count = 5;
    
    delta_y = (spread_height / (switch_count + 3));

    union()
    {
        difference()
        {
            cuboid([frame_width, frame_height, plate_depth], 
                fillet=mag_collar_diam / 2, edges=EDGES_Z_ALL);
            
            yspread(n=2, l=spread_height)
            xspread(n=2, l = spread_width)
            translate([0, 0, 
                plate_depth / 2 
                    - mag_collar_height / 2 + difference_fudge
            ])
            cyl(h=mag_collar_height, d = mag_collar_diam * 0.98);
            
            translate([0, 0, 
                plate_depth / 2 - acrylic_thickness / 2 + difference_fudge])
            cuboid([card_width, card_height, acrylic_thickness]);
            
            cuboid([
                card_width - frame_overlap * 2, 
                card_height - frame_overlap * 2, 
                plate_depth * 2], 
                fillet=card_overlap_fillet, edges=EDGES_Z_ALL);
            
            for (i = [1 : 1 : switch_count]) {
                x_offset = (i % 2) ? 1 : -1;
                
                y_offset = -spread_height / 2 + delta_y * (i + 1);
                
                color("silver")
                translate([
                    spread_width / 2 * x_offset,
                    y_offset, 
                    plate_depth / 2 
                        - trigger_mag_thickness / 2 
                        + difference_fudge
                ])
                cyl(h=trigger_mag_thickness, d = trigger_mag_diam);
               
            }
            
        }
        
        yspread(n=2, l=spread_height)
        xspread(n=2, l = spread_width)
        translate([0, 0, 
            plate_depth / 2 - mag_collar_height / 2 + difference_fudge])
        mag_collar();
    }
}

module front_plate_solid()
{
    spread_width = frame_width - mag_collar_diam;
    spread_height = frame_height - mag_collar_diam;
    switch_count = 5;
    
    delta_y = (spread_height / (switch_count + 3));

    front_plate_depth = mag_collar_height + print_layer_height * 7;
    front_collar_height = mag_collar_height + print_layer_height * 2;
    front_trigger_height = trigger_mag_thickness + print_layer_height * 2;

    difference()
    {
        cuboid([frame_width, frame_height, front_plate_depth], 
            fillet=mag_collar_diam / 2, edges=EDGES_Z_ALL);
        
        yspread(n=2, l=spread_height)
        xspread(n=2, l = spread_width)
        tz(front_plate_depth / 2 - front_collar_height / 2 + difference_fudge)
        cyl(h=front_collar_height, d = mag_diam + extrusion_fudge);
        
        for (i = [1 : 1 : switch_count]) {
            x_offset = (i % 2) ? 1 : -1;
            
            y_offset = -spread_height / 2 + delta_y * (i + 1);
            
            color("silver")
            translate([
                spread_width / 2 * x_offset,
                y_offset, 
                front_plate_depth / 2 
                    - front_trigger_height / 2 
                    + difference_fudge
            ])
            cyl(h=front_trigger_height, d = trigger_mag_diam + extrusion_fudge);
        }
    }
}

module plate_cover(include_triggers = false)
{
    spread_width = frame_width - mag_collar_diam;
    spread_height = frame_height - mag_collar_diam;
    switch_count = 5;
    
    delta_y = (spread_height / (switch_count + 3));

    front_collar_height = extra_mag_thickness - print_layer_height * 2;
    front_trigger_height = extra_mag_thickness - print_layer_height * 2;

    union()
    {
        cuboid([frame_width, frame_height, front_cover_depth], 
            fillet=mag_collar_diam / 2, edges=EDGES_Z_ALL);
        
        if(include_triggers) 
        {
            for (i = [1 : 1 : switch_count]) {
                x_offset = (i % 2) ? 1 : -1;
                
                y_offset = -spread_height / 2 + delta_y * (i + 1);
                
                color("silver")
                translate([
                    spread_width / 2 * x_offset,
                    y_offset, 
                    front_cover_depth / 2 
                        + front_trigger_height / 2 
                        - difference_fudge
                ])
                cyl(h=front_trigger_height, d = trigger_mag_diam - extrusion_fudge);
            }
        }
        
        yspread(n=2, l=spread_height)
        xspread(n=2, l = spread_width)
        translate([0, 0, 
            front_cover_depth / 2 + front_collar_height / 2 - difference_fudge])
        cyl(h=front_collar_height, d = mag_diam - extrusion_fudge);
    }
}

module printable()
{
    if(laser_cut) {
        projection()
        {
            translate([-50, 0, 0])
            bottom_half(z = led_collar_strip_slice_z - difference_fudge, s = 150)
            back_plate();

            translate([-100, 0, 0])
            top_half(z = led_collar_strip_slice_z - difference_fudge, s = 150)
            back_plate();
        }
    }
    else {
        if(show_back_plate) {
            translate([-50, 0, 0])
            bottom_half(z = led_collar_strip_slice_z - difference_fudge, s = 150)
            back_plate();

            translate([-100, 0, 0])
            zflip()
            top_half(z = led_collar_strip_slice_z - difference_fudge, s = 150)
            back_plate();
        }

        if(show_front_plate) {
            translate([50, 0, 0])
            front_plate_solid();

            translate([50, 100, 0])
            plate_cover(include_triggers = true);

            // translate([-50, 100, 0])
            // plate_cover();

        }
    }
}