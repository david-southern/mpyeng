include <BOSL2/std.scad>
include <BOSL2/shapes3d.scad>
include <useful-stuff.scad>

yrot($t * 360)
    empty_attachable_context([30, 20, 0.1], anchor=BOTTOM) {
        cube([30, 1, 0.1], anchor=BOTTOM);

        position(LEFT + FRONT) cubie(anchor=LEFT + FRONT + BOTTOM);

        position(RIGHT + BACK)
            xrot($t * 360)
                cube([1, 30, 0.1], anchor=BOTTOM) {
                    position(BACK)
                        cylie(anchor=CENTER);
                }
    }

module cubie(anchor = CENTER, spin = 0, orient = UP) {
    attachable(anchor, spin, orient, size=[10, 10, 3]) {
        cuboid([10, 10, 3], anchor=CENTER);
        children();
    }
}

module cylie(anchor = CENTER, spin = 0, orient = UP) {
    attachable(anchor, spin, orient, size=[10, 10, 3]) {
        cylinder(r=5, h=3, anchor=CENTER);
        children();
    }
}
