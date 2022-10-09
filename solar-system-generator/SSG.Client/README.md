BUILD/DEPLOY notes:

Building/Development:
* run `npm run watch` to start watch servers for webpack, sass and dotnet
* Debug in the Chrome devtools

To deploy:

- Create the release package:
- `dotnet publish -c Release`
- This step can take up to 10 minutes to complete
- Copy the contents of .\SSG.Client\bin\Release\net6.0\publish\wwwroot to the root of the ssg-demo repo
  - update the index.html to have the correct base: around line 8, change:
    - `<base href="/" />`
  - to this:
    - `<base href="/ssg-demo/" />`

- git add, commit, and push
- View the site at: `https://david-southern.github.io/ssg-demo/`

- To test a release package:
  - Go to the root of the ssg-demo repo
  - run `python3 -m http.server`
  - View the site at `http://localhost:8080`


TODOS:
Addl object settings:
- Perigee settings - center the orbit on the correct focus
- initial angular offset - orbital position at t=0
- "Comet" setting - allow for very large orbits that don't trigger the camera auto-zoom

Time mgmt:
- Allow time to run backwards
- Time slide range from -1 to 1, puase button to set to zero
- display current sim time

General:
- Download screenshot
- Help icons everywhere
- Popups close on click outside popup
- Get orbiter working
- Ability to look at a selected object
- Indicate current object selection
- Indicate current object selection

Settings:
- Quick settings: Speed, Zoom, View Angle
- Other settings in a full dialog behind an "Advanced" button

Other:
- Button to reset all settings to default
- Button to reset view to default
- Add planetary rings
- Add asteroid fields
- System Backgrounds
- Allow updating of planetary settings without resetting the entire simulation
- Add an "abstract units" setting - rather than having to use AU, etc. for units, just let the user put object radius =1, orbit radius = 5, etc.
- Pre-defined camera views - top down, side angle, side flat, etc.
- Animate camera transitions - lerp to another camera view
- Background needs to be a cube

Project:
- Add a C# "Units" helper - convert settings string like "1 AU" or "1 ER", "1 day", etc.back and forth to absolute sim units
- Rx C#?
- Threejs C# bindings?
- C# => JS interop - generate C# proxy classes from typescript typings?
