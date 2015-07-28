import processing.net.*;
import java.util.regex.*;
import java.util.*;

// External libraries. To install, select the menu Sketch | Import Library | Add Library
// Search for G4P and Shapes 3D
import shapes3d.*;
import shapes3d.animation.*;
import g4p_controls.*;

//Whole Object representation.
Sheep theSheep;
int currentPanel=0;
PShape selectedPanel;
HashMap<Integer, ArrayList<Integer>> partySideMap = new HashMap<Integer, ArrayList<Integer>>();
HashMap<Integer, ArrayList<Integer>> boringSideMap = new HashMap<Integer, ArrayList<Integer>>();

// Translates mouse inputs into camera movements
//PeasyCam cam;
Camera camera;

// network vars
int port = 4444;
Server _server; 
StringBuffer _buf = new StringBuffer();

PShape ground;

GButton btnGroundFront;
GButton btnGroundSide;
GButton btnGroundRear;


// setup() is called once by the environment to initialize things
void setup() {
  // This determines the size of the output window. Make it whatever
  // size feels good.
//  size(640, 360, P3D);
  size(1200, 800, P3D);
  
  // Some UI stuff. Need to get G4P up and running before PeasyCam
  btnGroundFront = new GButton(this, 5, 5, 50, 15, "Front Q");
  btnGroundSide = new GButton(this, 60, 5, 50, 15, "Side");
  btnGroundRear = new GButton(this, 115, 5, 50, 15, "Rear Q");
  
  // Initialize camera movements
  camera = new Camera(this, 0, -300, 500);
  
  // Load the .csv file which contains a mapping from logical panel
  // numbers used by the shows (and by the construction documents) into
  // surface indexes for the 3D model. Some panels map to up to 3 
  // surfaces (i.e. it's not strictly 1 to 1). The file is loaded twice,
  // once for each side.
  partySideMap = loadPolyMap("SheepPanelPolyMap.csv", "p");
  boringSideMap = loadPolyMap("SheepPanelPolyMap.csv", "b");

  // Most of the fun will happen in the sheep class, at least as far as 
  // display management goes.
  theSheep =  new Sheep(this, "model.obj");
  
  // Will use the ground when drawing. It is just a really big rectangle
  ground = createShape();
  ground.beginShape();
  ground.fill(#241906);
  ground.vertex(-10000,0,-10000);
  ground.vertex(10000,0,-10000);
  ground.vertex(10000,0,10000);
  ground.vertex(-10000,0,10000);
  ground.endShape(CLOSE);

  // The server is a TCP server listening on a defined port which accepts
  // commands from the lighting server to change the color of individual 
  // panels or to modify the parameters of the lights. It reads data into
  // a buffer which is periodically polled during the draw process.
  _server = new Server(this, port);
  println("server listening:" + _server);
}

// The draw() function can be considered the main event loop of the application.
// It's purpose is to draw the next frame onto the screen, and also to update
// any internal state that needs to change. It is called continously forever
// at whatever speed the rendering engine and host machine can handle.
void draw() {
  
  pushMatrix();
  // The last frame is not automatically cleared, so we do that first by
  // setting a solid background color.
  background(#1B2A36);
  camera.feed();

  // Draw the sheep surfaces in their current colors etc.
  theSheep.draw();
  
  shape(ground);
  
  // Also draw a center axis for general 3d reference. Red in +X axis,
  // Green in +Y, and Blue in +Z
  stroke(#ff0000);
  line(0, 0, 0, 10, 0, 0);
  stroke(#00ff00);
  line(0, 0, 0, 0, 10, 0);
  stroke(#0000ff);
  line(0, 0, 0, 0, 0, 10);
 
  // Check for any updates from the network. These won't be visible 
  // until the next time this function is called.
  pollServer();
  popMatrix();
  
  // Reset the camera for the UI elements
  perspective();
}

// Various mouse events to modify the camera in a reasonably natural feeling way
void mouseWheel(MouseEvent event) {
  float e = event.getCount();
  camera.zoom(e/10);
}

float dragArcScaling = 60;
float dragCircleScaling = 60;

void mouseDragged() {
  float x = (mouseX - pmouseX);
  float y = (mouseY - pmouseY);
  //println("x="+x+" y="+y);
  
  if (mouseButton == RIGHT) {
    camera.boom(y);
    camera.truck(x);
  } else if (mouseButton == CENTER) {
    camera.pan(x / dragCircleScaling);
    camera.tilt(y / dragArcScaling);
  } else {
    camera.circle(x / dragCircleScaling);
    camera.arc(y / dragArcScaling);
  }
  
  // Correct for being below ground
  float[] pos = camera.position();
  //println("camera y = "+pos[1]);
  if (pos[1] > -38f) {
    camera.jump(pos[0], -38f, pos[2]);
  }
}

// keyTyped is called outside of calls to the draw() function whenever
// a key is pressed and released, or possibly, depending on OS, it might
// be called multiple times if a key value is repeated. This is how we
// handle some simple UI input.
void keyTyped() {
  println("typed "+key);
  
  switch(key) {
    case 'n': // Next
      theSheep.moveCursor(1);
      println("Next panel = " + theSheep.panelCursor);
      break;
      
    case 'N': // Next
      theSheep.moveCursor(10);
      println("Next panel = " + theSheep.panelCursor);
      break;
      
    case 'p': // Prev
      theSheep.moveCursor(-1);
      println("Prev panel = " + theSheep.panelCursor);
      break;
      
    case 'P': // Prev
      theSheep.moveCursor(-10);
      println("Prev panel = " + theSheep.panelCursor);
      break;
  }

}

/**
 * Handle events from GButton buttons. Mostly we reset the display
 */
void handleButtonEvents(GButton button, GEvent event) {
  if (button == btnGroundFront) {
    camera.jump(-500, -50, 400);
    camera.aim(0,-200,0);
  } else if(button == btnGroundRear) {
    camera.jump(500, -60, 400);
    camera.aim(0,-100,0);
  } else if (button == btnGroundSide) {
    camera.jump(0, -300, 500);
    camera.aim(0,0,0);
  }
}
//
//public void handleToggleControlEvents(GToggleControl cb, GEvent event) {
//  if (cb == checkFreeRotate) {
//    if (cb.isSelected()) {
//      //cam.setFreeRotationMode();
//    } else {
//      //cam.setSuppressRollRotationMode();
//      //cam.setYawRotationMode();
//    }
//  }
//}

/**
 * Check the network server for waiting data and make any necessary
 * state changes based on pending commands.
 */
void pollServer() {
  try {
    // Get the current client (if any)
    Client c = _server.available();
    // append any available bytes to the buffer
    if (c != null) {
      // Put all we have into this buffer not worrying at this point
      // about it potentially being a partial line or multiple lines.
      // Just bytes into buffer.
      _buf.append(c.readString());
    }
    
    // process as many lines as we can find in the buffer. Lines are
    // terminated with \n characters so we break the string apart into
    // lines first, and then call processCommand to deal with each line,
    // until there are no more complete lines - although there might be
    // some partial part of a line hanging out in the buffer waiting
    // to get completed by new data on the next time through here.
    int ix = _buf.indexOf("\n");
    while (ix > -1) {
      String msg = _buf.substring(0, ix);
      msg = msg.trim();
      //println(msg);
      processCommand(msg);
      _buf.delete(0, ix+1);
      ix = _buf.indexOf("\n");
    }
  } 
  catch (Exception e) {
    println("exception handling network command");
    e.printStackTrace();
  }
}

// This regular expression is used to parse anything that doesn't appear to be a DMX
// command. The DMX syntax is handled by the second expression
Pattern cmd_pattern = Pattern.compile("^\\s*(p|b|a|f )\\s+(\\d+)\\s+(\\d+),(\\d+),(\\d+)\\s*$");

Pattern dmx_pattern = Pattern.compile("^\\s*dmx\\s+(\\d+)\\s+(\\d+)\\s*$");

void processCommand(String cmd) {
  Matcher m = cmd_pattern.matcher(cmd);
  if (!m.find()) {
    m = dmx_pattern.matcher(cmd);
    if (m.find()) {
      handleDMXCommand(m);
      return;
    }
    
    println("Input was malformed, please conform to \"[a,p,b,f] panelId r,g,b\" where a=all sides, b=boring, p=party, f=flood, panelId = numeric value, r,g, and b are red green and blue values between 0 and 255");
    return;
  }
  
  String side = m.group(1);
  int panel = Integer.valueOf(m.group(2));
  int r    = Integer.valueOf(m.group(3));
  int g    = Integer.valueOf(m.group(4));
  int b    = Integer.valueOf(m.group(5));

  //System.out.println("side:"+side+" "+String.format("panel:%d to r:%d g:%d b:%d", panel, r, g, b));
  
  if (r < 0 || r > 255 || g < 0 || g > 255 || b < 0 || b > 255 ) {
     System.out.println("Bypassing last entry because an r,g,b value was not between 0 and 255:"+r+","+g+","+b); 
     return;
  }

  theSheep.setPanelColor(side, panel, color(r, g, b));
}

void handleDMXCommand(Matcher m) {
  try {
    int channel = Integer.valueOf(m.group(1));
    int value = Integer.valueOf(m.group(2));
    
    // DMX is inherently broadcast, so just do that and let each eye be responsible for
    // deciding if it cares or not.
    theSheep.leftEye.handleDMX(channel, value);
    theSheep.rightEye.handleDMX(channel, value);
  } catch (Exception e) {
    // Don't care much about handling integer parsing errors, but they are no reason to crash
    println(e);
  }
}

/*
 * Load label mapping file
 */
HashMap<Integer, ArrayList<Integer>> loadPolyMap(String labelFile, String sidePorB) {
  HashMap<Integer, ArrayList<Integer>> polyMap = new HashMap<Integer, ArrayList<Integer>>();  
  Table table = loadTable(labelFile);

  println(table.getRowCount() + " total rows in table"); 

  for (TableRow row : table.rows ()) {
    if (row.getString(4).equals(sidePorB)) {
      ArrayList<Integer> temp = new ArrayList<Integer>();
      int panel = row.getInt(0);

      temp.add(row.getInt(1));
      temp.add(row.getInt(2)); 
      temp.add(row.getInt(3));

      polyMap.put(panel, temp);
    }
  }
  return polyMap;
}

void invertShape(PShape shape) {
  if (shape==null) return;
  
  for(int i=0; i<shape.getVertexCount(); i++) {
    shape.setVertex(i, shape.getVertexX(i), shape.getVertexY(i), -1 * shape.getVertexZ(i));
  }
}

class Sheep {

  PShape sheepModel;
  PShape[] sheepPanelArray;

  Eye leftEye;
  Eye rightEye;
  
  int panelCursor;

  public Sheep(PApplet app, String fileName) {
    sheepModel = loadShape(fileName); 
//
//    int[] divColors = {
//color(141,211,199),color(255,255,179),color(190,186,218),color(251,128,114),color(128,177,211),color(253,180,98),color(179,222,105),color(252,205,229),color(217,217,217),color(188,128,189),color(204,235,197),color(255,237,111)
//    };
//    
//    PShape[] kids = sheepModel.getChildren();
//    int cIx = 0;
//    for(int i=0; i<kids.length; i++) {
//      PShape shape = kids[i];
//      if (shape == null) continue;
//      
//      println(shape.getName());
//      // Inverting the model seems necessary
//      invertShape(shape);
//
//      if (i < 10) {
//        // Tail
//        shape.setStroke(true);
//        shape.setStroke(#808080);
//        shape.setStrokeWeight(1f);
//        shape.setFill(#303030);
//      } else {
//        if (i < 40) {
//          shape.setStroke(true);
//          shape.setStroke(#ff0000);
//          shape.setStrokeWeight(4f);
//        }
//        
//        shape.setFill(divColors[cIx++]);
//        if (cIx == divColors.length) {
//          cIx = 0;
//        }
//      }
//    }

    sheepPanelArray = sheepModel.getChildren();
    
    // Darken unmapped surfaces
    HashSet<Integer> all = new HashSet<Integer>();
    for(Map.Entry entry: partySideMap.entrySet()) {
      ArrayList<Integer> list = (ArrayList<Integer>)entry.getValue();
      for(int i: list) {
        all.add(i);
      }
    }
    for(Map.Entry entry: boringSideMap.entrySet()) {
      ArrayList<Integer> list = (ArrayList<Integer>)entry.getValue();
      for(int i: list) {
        all.add(i);
      }
    }
    for(int i=0; i<sheepPanelArray.length; i++) {
      PShape shape = sheepPanelArray[i];
      if (shape == null) continue;
      
      // Must invert all shapes
      invertShape(shape);
   
      // If it's an unmapped shape, make it dark
      if (!all.contains(i)) {
        shape.setStroke(true);
        shape.setStroke(#808080);
        shape.setStrokeWeight(1f);
        shape.setFill(#303030);
      }
    }

    sheepModel.rotateX(PI);
    sheepModel.rotateY(PI*0.5);
    sheepModel.translate(30, 10, 550); // Shit, still in model coord space. Lame!
    
    leftEye = new Eye(app, "Left eye", 400, new PVector(-135, -215, 27));
    rightEye = new Eye(app, "Right eye", 416, new PVector(-135, -215, -27));
    
  }

  void setPanelColor(String side, int panel, color c) {
    ArrayList<Integer> polygons = new ArrayList<Integer>();
    if (side.equals("p") && partySideMap.get(panel) != null) {
      polygons.addAll(partySideMap.get(panel));
    } else if (side.equals("b") && boringSideMap.get(panel) != null) {
      polygons.addAll(boringSideMap.get(panel));
    } else if (side.equals("a")) {
      if (partySideMap.get(panel) != null) {
        polygons.addAll(partySideMap.get(panel));
      }
      if (boringSideMap.get(panel) != null) {
          polygons.addAll(boringSideMap.get(panel));
      }
    } else if (side.equals("f")) {
      Iterator partyItr = partySideMap.keySet().iterator();
      
      while (partyItr.hasNext()) {
         polygons.addAll(partySideMap.get(partyItr.next())); 
      }
      
      Iterator boringItr = boringSideMap.keySet().iterator();
      
      while (boringItr.hasNext()) {
         polygons.addAll(boringSideMap.get(boringItr.next())); 
      }
      
    
    }      

    if (polygons != null && polygons.size() > 0) {
      for (Integer polygon : polygons) {
  
        if (polygon != null && polygon != -1) {
          sheepPanelArray[polygon].setFill(c);
//          sheepPanelArray[polygon].disableStyle();
//  
//          fill(c);
//  
//          shape(sheepPanelArray[polygon]);
        }
      }
    } else {
       System.out.println("Panel number was not found in map.  Bypassing command."); 
    }
  } // end setPanelColor
  
  public void moveCursor(int direction) {
    int prev = panelCursor;
    
    panelCursor += direction;
    if (panelCursor >= sheepPanelArray.length) {
      panelCursor -= sheepPanelArray.length;
    } else if (panelCursor < 0) {
      panelCursor += sheepPanelArray.length;
    }        
  }
  
  public void draw() {
    // Wrapping this draw in push & pop matrix means that any
    // visual changes we make here (such as camera position,
    // rotation, etc.) won't be left hanging around when this
    // function returns.
    pushMatrix();
    
    // To draw the sheep using the current style of every panel,
    // we only need a single shape call.
    shape(sheepModel);

    // The eyes also have to get rendered. They are not part of
    // the loaded model but were added later
    leftEye.draw();
    rightEye.draw();
    
    // Finally (for the sheep at least) we re-render one surface
    // in a different color. Do this by re-rendering rather than 
    // changing the style so that we don't loose the style for this
    // surface just because the cursor traversed it.
    PShape curPanel = sheepPanelArray[panelCursor];
    if (curPanel != null) {
      sheepPanelArray[panelCursor].disableStyle(); 
      fill(0xff00ff00);
      shape(sheepPanelArray[panelCursor]);
      sheepPanelArray[panelCursor].enableStyle(); 
    }
    
    // This restores the matrix that was pushed at the beginning of 
    // this function.
    popMatrix();
  }
  
  /**
   * An instance of Eye represents one of the DMX controlled sharpies. Using 16 channel
   * mode.
   */
  class Eye {
    // These are all byte values, but because of not having unsigned ints
    // in java it is easiest to make them ints and then treat them as byte range (0-255)
    // instead of trying to deal with signed bytes.
    //
    // There are only 16 channels, but DMX is 1 based, not 0 based, in all the manuals, so
    // to preserve numbering we effectively make these 1-based indexes by expanding their
    // size.
    int[] channelValues = new int[17];

    // We mostly need these for PAN that can wrap at 540 degrees of movement, but just
    // keep them for all    
    int[] currentValues = new int[17];
    
    boolean dmxDirty;
    int dmxOffset;
    
    Cone cone;
    
    StopWatch watch;
    final float ANIMATION_TIME = 10.0f;
    final float BEAM_LENGTH = 1000;
    final float BEAM_MAX_SPOT = 50;
    boolean nextIsPan;
    
    final int DMX_PAN = 1;
    final int DMX_PAN_FINE = 2;
    final int DMX_TILT = 3;
    final int DMX_TILT_FINE = 4;
    final int DMX_COLOR_WHEEL = 5;
    final int DMX_STROBE = 6;
    final int DMX_DIMMER = 7;
    final int DMX_GOBO = 8;
    final int DMX_EFFECT = 9;
    final int DMX_LADDER_PRISM = 10;
    final int DMX_8_FACET_PRISM = 11;
    final int DMX_3_FACET_PRISM = 12;
    final int DMX_FOCUS = 13;
    final int DMX_FROST = 14;
    final int DMX_PAN_TILT_SPEED = 15;
    final int DMX_RESET_AND_LAMP = 16;
    
    String me;
    
    Eye(PApplet app, String me, int dmx, PVector position) {
      this.me = me;
      this.dmxOffset = dmx;
      
      watch = new StopWatch();
      
      cone = new Cone(app, 40, new PVector(0, 1, 0), new PVector(0, BEAM_LENGTH, 0));
      cone.setSize(BEAM_MAX_SPOT, BEAM_MAX_SPOT, BEAM_LENGTH);
      cone.moveTo(position);
      cone.fill(0x80ffff00);
      cone.drawMode(Shape3D.SOLID);
      
      // Some beginning values for DMX
      channelValues[DMX_PAN] = 128;
      channelValues[DMX_TILT] = 128;
      channelValues[DMX_DIMMER] = 128;
      dmxDirty = true;
    }
    
    public void draw() {
      watch.update();
      
      // Do all our DMX state updates here at the beginning of each draw cycle. They
      // often won't have changed, hence the dirty flag, but it seems to make sense
      // to only update recalculate things after they have changed
      if (dmxDirty) {
        updateDMX();
      }
      
      cone.draw();
      
//      if (watch.currTime() > ANIMATION_TIME) {
//        watch.reset();
//        
//        if (nextIsPan) {
//          cone.rotateBy(0f, 0f, 2 * PI, ANIMATION_TIME, 0.0f);
//        } else {
//          cone.rotateBy(2 * PI, 0f, 0f, ANIMATION_TIME, 0.0f);
//        }
//        
//        nextIsPan = !nextIsPan;
//      }
    }
    
    // Don't have exact specs so from Sharpy we get max speed pan 2.45s, tilt 1.30s 
    // For Super sharpy PAN fast = 3.301s, normal = 4.038s
    //                  TILT fast = 2.060, normal = 2.274s
    // Call it 3 s for max pan, and 1.8s for max tilt. Really should measure I guess... 
    final int MAX_PAN_PER_SECOND = (int)((float)0x0000ffff / 3.0f);
    final int MAX_TILT_PER_SECOND = (int)((float)0x0000ffff / 1.8f);
    
    final float PAN_CONVERSION = (3 * PI) / (float)(0x0000ffff);
    final float TILT_CONVERSION = (1.5 * PI) / (float)(0x0000ffff);

    private void updateDMX() {
      //println("Updating DMX");
      // Set to false now, but reset to true if we don't achieve our goals for animated things
      // like pan & tilt
      dmxDirty = false;
      
      updatePan();
      updateTilt();
      
      updateColorWheel();
    }
    
    /**
     * Looks at the current vs. channel values for pan and moves the beam towards the
     * desired position, but only at the maximum allowed speed.
     */
    private void updatePan() {
      // Positioning - Pan & Tilt.
      // 16-bit control spread across two DMX channels. 540 degrees for pan, 270 for tilt.
      if (currentValues[DMX_PAN] != channelValues[DMX_PAN] || currentValues[DMX_PAN_FINE] != channelValues[DMX_PAN_FINE]) {
        // Must update pan from current towards channel
        int currentPan = ((currentValues[DMX_PAN] << 8) & 0x0000ff00) + currentValues[DMX_PAN_FINE];
        int channelPan = ((channelValues[DMX_PAN] << 8) & 0x0000ff00) + channelValues[DMX_PAN_FINE];
        
        //println("currentPan = "+currentPan+"  channelPan="+channelPan);
        
        // We lose a tiny amount of precision with rounding into a 16-bit integer
        // space, but it's pretty irrelevant for our purposes
        int maxPan = (int)(MAX_PAN_PER_SECOND * watch.lapTime());
        
        int delta = channelPan - currentPan;
        //println("maxPan = "+maxPan + "  delta = "+delta);
        if (delta > maxPan) {
          delta = maxPan;
          dmxDirty = true;
        } else if (delta < -maxPan) {
          delta = -maxPan;
          dmxDirty = true;
        }
        
        // Save the new position
        currentPan += delta;
        //println("Saving currentPan of "+currentPan);
        currentValues[DMX_PAN] = (currentPan >> 8 ) & 0x00ff;
        currentValues[DMX_PAN_FINE] = currentPan & 0x00ff;
        
        // Position the beam at this rotation
        cone.rotateToX(-1 * (PAN_CONVERSION * currentPan - HALF_PI));
      }
    }

    /**
     * Like updatePan, but for tilt
     */
    private void updateTilt() {
      // Positioning - Pan & Tilt.
      // 16-bit control spread across two DMX channels. 540 degrees for pan, 270 for tilt.
      if (currentValues[DMX_TILT] != channelValues[DMX_TILT] || currentValues[DMX_TILT_FINE] != channelValues[DMX_TILT_FINE]) {
        // Must update pan from current towards channel
        int current = ((currentValues[DMX_TILT] << 8) & 0x0000ff00) + currentValues[DMX_TILT_FINE];
        int channel = ((channelValues[DMX_TILT] << 8) & 0x0000ff00) + channelValues[DMX_TILT_FINE];
        
        //println("currentPan = "+currentPan+"  channelPan="+channelPan);
        
        // We lose a tiny amount of precision with rounding into a 16-bit integer
        // space, but it's pretty irrelevant for our purposes
        int max = (int)(MAX_TILT_PER_SECOND * watch.lapTime());
        
        int delta = channel - current;
        if (delta > max) {
          delta = max;
          dmxDirty = true;
        } else if (delta < -max) {
          delta = -max;
          dmxDirty = true;
        }
        
        // Save the new position
        current += delta;
        //println("Saving currentTilt of "+current);
        currentValues[DMX_TILT] = (current >> 8 ) & 0x00ff;
        currentValues[DMX_TILT_FINE] = current & 0x00ff;
        
        // Position the beam at this rotation
        cone.rotateToZ(TILT_CONVERSION * current - QUARTER_PI);
      }
    }
    
    private void updateColorWheel() {
      // TODO: Make this an animated property, possibly with a texture so that intermediate
      // color values where you get 2 colors on the wheel at the same time are visualizable
      int c = channelValues[DMX_COLOR_WHEEL];
      int clr = #ffffff;
      
      if (c < 9) {
        // Open / White
        clr = #ffffff;
      } else if (c < 17) {
        // Color 1 - Dark red
//        clr = #840000;
        clr = #e50000;
      } else if (c < 25) {
        // Color 2 - Orange
        clr = #f97306;
      } else if (c < 33) {
        // Color 3 - Aquamarine
        clr = #04d8b2;
      } else if (c < 41) {
        // Color 4 - Deep Green
//        clr = #02590f;
        clr = #15b01a;
      } else if (c < 49) {
        // Color 5 - Light green
        clr = #96f97b;
      } else if (c < 57) {
        // Color 6 - Lavender
        clr = #c79fef;
      } else if (c < 66) {
        // Color 7 - Pink
        clr = #ff81c0;
      } else if (c < 74) {
        // Color 8 - Yellow
        clr = #ffff14;
      } else if (c < 83) {
        // Color 9 - Magenta
        clr = #c20078;
      } else if (c < 92) {
        // Color 10 - Cyan
        clr = #00ffff;
      } else if (c < 101) {
        // Color 11 - CTO2
        clr = #FFF9ED;
      } else if (c < 110) {
        // Color 12 - CTO1
        clr = #FFF3D8;
      } else if (c < 119) {
        // Color 13 - CTB
        clr = #F7FBFF;
      } else if (c < 128) {
        // Color 14 - Dark Blue
        //clr = #00035b;
        clr = #0343df;
      }
      
      // Multiple times a dimmer byte
      int brightness = channelValues[DMX_DIMMER] & 0x00ff;
//      int r = ( ((clr & 0x00ff0000) >> 16) * brightness ) >> 8;
//      int g = ( ((clr & 0x0000ff00) >>  8) * brightness ) >> 8;
//      int b = ( ((clr & 0x000000ff)      ) * brightness ) >> 8;
//      
//      clr = ((r << 16) & 0x00ff0000) | 
//            ((g <<  8) & 0x0000ff00) |
//            ((b      ) & 0x000000ff) |
//            0xc0000000;
      clr = ((brightness << 24 ) & 0xff000000) | (clr & 0x00ffffff);
      cone.fill(clr, Cone.ALL);
      
      currentValues[DMX_COLOR_WHEEL] = c;
    }
    
    public void handleDMX(int channel, int value) {
      
      if (channel < dmxOffset || channel > (dmxOffset + 15)) {
        // Not for us
        return;
      }
      
      if (value < 0) {
        //println("Capping value "+value+" at 0");
        value = 0;
      } else if (value > 255) {
        //println("Capping value "+value+" at 255");
        value = 255;
      }
      
      // The dmxOffset defines what is referred to as "channel 1", so
      // we have to have array that start at 1, not 0, so we add that 1 back
      channel -= dmxOffset;
      channel++;
      channelValues[channel] = value;
      
      // println(me + " setting dmx "+channel+" to "+value);
      dmxDirty = true;
    }
  }
}

