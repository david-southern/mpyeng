include <BOSL/constants.scad>
use <BOSL/shapes.scad>
use <BOSL/transforms.scad>

$fn = 43;

// back_plate();
front_plate();

difference_fudge = 0.01;
extrusion_fudge = 0.1;
print_layer_height = 0.15;
wall_thickness = 2;

acrylic_thickness = 3.25;

mag_diam = 8 + extrusion_fudge * 2;
mag_thickness = 3;

frame_xside_width = 12;
frame_yside_width = 14;
mag_frame_offset = 4;

frame_overlap = 2;

card_width = 54;
card_height = 81;
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

mag_projection_depth = (3/16) * 25.4;
mag_collar_diam = mag_diam + mag_frame_offset;

strip_width = 12.5;
strip_height = 1.7;
led_width = 5.2;
led_height = 2.1;

module mag_collar()
{
    difference()
    {
        color("black")
        cyl(h=mag_projection_depth, d=mag_collar_diam);
        
        color("silver")
        translate([0, 0, 
            mag_projection_depth / 2 - mag_thickness / 2 + difference_fudge])
            cyl(h=mag_thickness, d=mag_diam);        
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

spread_width = frame_width - mag_collar_diam;
spread_height = frame_height - mag_collar_diam;
switch_count = 5;

delta_y = (spread_height / (switch_count + 3));

module back_plate()
{
    signal_connector_length = spread_width / 2 - reed_cutout_length;

    difference()
    {
        union()
        {
            cuboid([frame_width, frame_height, plate_depth], 
                fillet=mag_collar_diam / 2, edges=EDGES_Z_ALL);
            
            yspread(n=2, l=spread_height)
            xspread(n=2, l = spread_width)
            translate([0, 0, 
                plate_depth / 2 + mag_projection_depth / 2 - difference_fudge])
            mag_collar();
        }
        
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
            
            color("silver")
            translate([
                signal_connector_length / 2 * x_offset, 
                y_offset, 
                -plate_depth / 2 
            ])
            xcyl(h = signal_connector_length, d=wire_diam);
        }
        
        signal_line_length = frame_height + difference_fudge * 2;
        
        color("silver")
        translate([0, 0, -plate_depth / 2])
        ycyl(h = signal_line_length, d=wire_diam);
        
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
                plate_depth / 2 - mag_projection_depth / 2 + difference_fudge])
            cyl(h=mag_projection_depth, d = mag_collar_diam * 0.98);
            
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
                
                color("silver")
                translate([
                    signal_connector_length / 2 * x_offset, 
                    y_offset, 
                    -plate_depth / 2 
                ])
                xcyl(h = signal_connector_length, d=wire_diam);
            }
            
        }
        
        yspread(n=2, l=spread_height)
        xspread(n=2, l = spread_width)
        translate([0, 0, 
            plate_depth / 2 - mag_projection_depth / 2 + difference_fudge])
        mag_collar();
    }
}































