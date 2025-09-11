include <BOSL2/std.scad>
use <lazy.scad>

$fn = 83;

core_one_bed_width = 240;

// Parameters
tray_width = 64; // Width of the pixel strip tray
tray_wiring_channel_width = 10; // Width of the channel for wiring
tray_height = 15; // Height of the pixel strip tray

lip_depth = 7; // Depth of the lip that holds the tray in place
lip_height = 7; // Height of the lip that holds the tray in place

collar_width_x = 4; // Width of the collar around the outer edge
collar_width_y = 10; // Height of the collar around the outer edge

outer_width = tray_width + tray_wiring_channel_width * 2 + collar_width_x * 2;    // Width of outer block
outer_depth = lip_depth + collar_width_y;    // Depth of outer block
outer_height = tray_height + lip_height;   // Height of outer block

echo(str("outer_width=", outer_width, " outer_depth=", outer_depth, " outer_height=", outer_height));

corner_radius = 3;

support_pin_diameter = 4;
support_pin_height = 7;

split_height_percentage = 0.5;
split_depth_percentage = 0.5;

epsilon = 0.01; // Small value to ensure proper subtraction

module rounded_box(size, radius) {
    minkowski() {
        cube(size - [2*radius, 2*radius, 2*radius], center=true);
        sphere(r=radius, $fn=83);
    }
}

module collar_half() {
    difference() {
        // Outer rounded box
        translate([0, 0, 0]) rounded_box([outer_width, outer_depth, outer_height], corner_radius);

        // Inner cavity
        color("red")
        translate([0, 0, 0]) cube([
            tray_width + tray_wiring_channel_width * 2,
            lip_depth,
            tray_height
        ], center=true);

        // Split vertically
        translate([-outer_width, -outer_depth, -outer_height / 2 - epsilon])
            cube([2*outer_width, 2*outer_depth, outer_height * split_height_percentage], center=false);

        // Split front to back
        translate([-outer_width, -outer_depth / 2 - epsilon, -outer_height])
            cube([2*outer_width, outer_depth * split_depth_percentage, outer_height * 2], center=false);
    }

    // Support pins
    pin_spacing = (outer_width - (outer_width - tray_width)) / 2;
    xcopies(pin_spacing, 3)
    tz(-support_pin_height/2 + epsilon)
    ty((outer_depth + lip_depth) / 4)
    cylinder(h=support_pin_height, r=support_pin_diameter/2, center=true);
}

collar_half();
