//
//   SHIT TO START WITH
//
//   Did you install the external libraries yet?
//       - Use the Sketch menu -> Import Library -> Add Library
//       - Search for G4P - Click Install
//       - Search for Shapes - Click Install on Shapes 3D
//
//   It should run now. Hit the play button in the upper left corner of this window.
//
//   OMG! Is that window too F-ing big???  Change these two numbers right here
//   to something smaller for your tiny little screen. Try a width of 640 and a
//   height of 480 as if your computer is from 1993.
//                          |
//                          V
final int WINDOW_WIDTH  = 1200;
final int WINDOW_HEIGHT =  800;

//
//   After you change those numbers you have to hit the stop button and then the
//   play button again to restart things.
//
//   Now go start the python server to make the colors change.
//
//   Enjoy. (BTW - try dragging with your mouse in the simulator window. 
//   That will move the camera around.)
//
//   If things totally don't work, feel free to bug Tom Seago via facebook
//   or via email <tom@tomseago.com>.  I promise to make up as many answers 
//   as you want.
//

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
TreeMap<Integer, ArrayList<Integer>> partySideMap = new TreeMap<Integer, ArrayList<Integer>>();
TreeMap<Integer, ArrayList<Integer>> boringSideMap = new TreeMap<Integer, ArrayList<Integer>>();

Camera camera;

// network vars
int port = 4444;
Server _server; 
StringBuffer _buf = new StringBuffer();

// TODO: The ground should probably be a Shapes3D terrain. Whatevs.
PShape ground;

GButton btnGroundFront;
GButton btnGroundSide;
GButton btnGroundRear;
GButton btnHighNext;
GButton btnHighPrev;

GCheckbox cbShowLabels;
GCheckbox cbLogicalHighlight;

GLabel lblHighNum;

GButton btnColors;

// This scale is applied to the loaded OBJ and then everything else that
// was originally scaled relative to the baseline OBJ. The issue was that
// at the original scale, all the font sizes were tiny, and apparently they
// get prerendered to surfaces because they came out extra fuzzy and crappy.
// Scaling everything up seems to have resolved that.
final int SHEEP_SCALE = 3;


// setup() is called once by the environment to initialize things
void setup() {
  size(1200, 800, P3D);
  
  // Some UI stuff. Need to get G4P up and running before PeasyCam
  G4P.setGlobalColorScheme(G4P.YELLOW_SCHEME);
  btnGroundFront = new GButton(this, 5, 5, 50, 15, "Front Q");
  btnGroundSide = new GButton(this, 60, 5, 50, 15, "Side");
  btnGroundRear = new GButton(this, 115, 5, 50, 15, "Rear Q");
  cbShowLabels = new GCheckbox(this, 5, 25, 100, 15, "Show Labels");

  cbLogicalHighlight = new GCheckbox(this, 5, 45, 300, 15, "Show Highlight");
  btnHighPrev = new GButton(this, 5, 65, 50, 15, "Prev");
  btnHighNext = new GButton(this, 60, 65, 50, 15, "Next");
  
  lblHighNum = new GLabel(this, 115, 65, 30, 15, "1");
  
  btnColors = new GButton(this, 5, 85, 120, 15, "Constrasting Colors");
  
  // Initialize camera movements
  camera = new Camera(this, 0, SHEEP_SCALE * -300, SHEEP_SCALE * 500);
  
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
  ground.vertex(SHEEP_SCALE * -10000,0,SHEEP_SCALE * -10000);
  ground.vertex(SHEEP_SCALE * 10000,0,SHEEP_SCALE * -10000);
  ground.vertex(SHEEP_SCALE * 10000,0,SHEEP_SCALE * 10000);
  ground.vertex(SHEEP_SCALE * -10000,0,SHEEP_SCALE * 10000);
  ground.endShape(CLOSE);
  
  // let's start with contrasting colors because they are prettier
  theSheep.setContrastingColors();

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
  line(0, 0, 0, SHEEP_SCALE * 10, 0, 0);
  stroke(#00ff00);
  line(0, 0, 0, 0, SHEEP_SCALE * 10, 0);
  stroke(#0000ff);
  line(0, 0, 0, 0, 0, SHEEP_SCALE * 10);
 
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

  if (keyCode == SHIFT) {
    camera.zoom(e/10);
  } else {    
    camera.dolly(e*4);
  }
}

float dragArcScaling = 60;
float dragCircleScaling = 60;

void mouseDragged() {
  float x = (mouseX - pmouseX);
  float y = (mouseY - pmouseY);
  //println("x="+x+" y="+y);
  
 
  if (mouseButton == CENTER || keyCode == SHIFT) {
    camera.boom(y*4);
    camera.truck(x*4);
  } else if (mouseButton == RIGHT) {
    camera.pan(x / dragCircleScaling);
    camera.tilt(y / dragArcScaling);
  } else {
    // LEFT
    camera.circle(-x / dragCircleScaling);
    camera.arc(y / dragArcScaling);
  }
  
  // Correct for being below ground
  float[] pos = camera.position();
  //println("camera y = "+pos[1]);
  if (pos[1] > -38f) {
    camera.jump(pos[0], -38f, pos[2]);
  }
}

StringBuffer panelValue = new StringBuffer();

// keyTyped is called outside of calls to the draw() function whenever
// a key is pressed and released, or possibly, depending on OS, it might
// be called multiple times if a key value is repeated. This is how we
// handle some simple UI input.
void keyTyped() {
  println("typed "+key);
  
  switch(key) {
    case '.': // Next
      theSheep.moveCursor(1);
      println("Next panel = " + theSheep.panelCursor);
      break;
      
    case '>': // Next
      theSheep.moveCursor(10);
      println("Next panel = " + theSheep.panelCursor);
      break;
      
    case ',': // Prev
      theSheep.moveCursor(-1);
      println("Prev panel = " + theSheep.panelCursor);
      break;
      
    case '<': // Prev
      theSheep.moveCursor(-10);
      println("Prev panel = " + theSheep.panelCursor);
      break;

    // The logical cursor
    case ']': // Next
      theSheep.moveLogicalCursor(1);
      updateHighlightNumber();
      break;
      
    case '}': // Next
      theSheep.moveLogicalCursor(10);
      updateHighlightNumber();
      break;
      
    case '[': // Prev
      theSheep.moveLogicalCursor(-1);
      updateHighlightNumber();
      break;
      
    case '{': // Prev
      theSheep.moveLogicalCursor(-10);
      updateHighlightNumber();
      break;
      

    case 'p': // Assign to P side
      assignPanel(true);
      break;
      
    case 'b': // Assignt to B side
      assignPanel(false);
      break;
      
    case 's': // Save to a file
      savePanelMap();
      break;
      
    default:
      if (key >= '0' && key <= '9') {
        panelValue.append(key);
      }    
  }
}

// Assign the current surface to the logical panel in panelValue, assuming it can
// be parsed as an int
void assignPanel(boolean isParty) {
  if (panelValue.length()==0) {
    println("Type some digits. Nothing to assign");
    return;
  }
  
  int logicalNum = -1;
  String toParse = panelValue.toString();
  panelValue.setLength(0);
  try {
    logicalNum = Integer.parseInt(toParse);
  } catch (NumberFormatException nfe) {
    println("Could not parse '"+toParse+"' as a number");
    return;
  }
  
  // First remove this from any logical assignment it might have. THis is slow and bad
  // and brute force, but that's not important to us right now
  clearAssignment(partySideMap);
  clearAssignment(boringSideMap);
  
  TreeMap<Integer, ArrayList<Integer>> map = isParty ? partySideMap : boringSideMap;
  ArrayList<Integer> list = map.get(logicalNum);
  if (list==null) {
    list = new ArrayList<Integer>();
    map.put(logicalNum, list);
  }
  
  list.add(theSheep.panelCursor);
  println("Assigned surface "+theSheep.panelCursor+" to logical panel "+logicalNum+" on "+(isParty?"party":"business")+" side");
}

void clearAssignment(TreeMap<Integer, ArrayList<Integer>> map) {
  Integer toKill = new Integer(theSheep.panelCursor);
  for(ArrayList<Integer> list: map.values()) {
    while(list.remove(toKill));
  }
}

void savePanelMap() {
  String filename = "saved-panel-map.csv";
  PrintWriter out = createWriter(filename);
  
  for(Map.Entry e: partySideMap.entrySet()) {
    writeLine(out, e, "p");
  }
  out.println();
  
  for(Map.Entry e: boringSideMap.entrySet()) {
    writeLine(out, e, "b");
  }
  
  out.flush();
  out.close();
  
  println("Saved current map to "+filename);
}

void writeLine(PrintWriter out, Map.Entry e, String side) {

    out.print((Integer)e.getKey());
    out.print(",");
    
    for(Integer i: (ArrayList<Integer>)e.getValue()) {
      out.print(i);
      out.print(",");
    }
    
    out.print(side);
    out.print("\n");
}

/**
 * Handle events from GButton buttons. Mostly we reset the display
 */
void handleButtonEvents(GButton button, GEvent event) {
  if (button == btnGroundFront) {
    camera.jump(SHEEP_SCALE * -500, SHEEP_SCALE * -50, SHEEP_SCALE * 400);
    camera.aim(0,SHEEP_SCALE * -200,0);
  } else if(button == btnGroundRear) {
    camera.jump(SHEEP_SCALE * 500, SHEEP_SCALE * -60, SHEEP_SCALE * 400);
    camera.aim(0,SHEEP_SCALE * -100,0);
  } else if (button == btnGroundSide) {
    camera.jump(0, SHEEP_SCALE * -300, SHEEP_SCALE * 500);
    camera.aim(0,0,0);
  } else if (button == btnHighNext) {
    theSheep.moveLogicalCursor(1);
    updateHighlightNumber();
  } else if (button == btnHighPrev) {
    theSheep.moveLogicalCursor(-1);
    updateHighlightNumber();
  } else if (button == btnColors) {
    theSheep.setContrastingColors();
  }
}

public void handleToggleControlEvents(GToggleControl cb, GEvent event) {
  if (cb == cbShowLabels) {
    theSheep.setShowLabels(cb.isSelected());
  } else if (cb == cbLogicalHighlight) {
    theSheep.showLogicalHighlight = cb.isSelected();
  }
}

public void updateHighlightNumber() {
  lblHighNum.setText(Integer.toString(theSheep.logicalCursor));
}

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
    
    // TODO: Make this handle more than one DMX value per line.
    // TODO: Make this map DMX for the panel colors back onto panels. - low priority
    
    // DMX is inherently broadcast, so just do that and let each eye be responsible for
    // deciding if it cares or not.
    theSheep.leftEye.handleDMX(channel, value);
    theSheep.rightEye.handleDMX(channel, value);
  } catch (Exception e) {
    // Don't care much about handling integer parsing errors, but they are no reason to crash
    println(e);
  }
}

/**
 * Loads the mapping file to go from logical panel identifiers to integer indexes
 * of surfaces in the 3D mesh. The file is filtered to only load one side at a time
 * as specified by the last parameter.
 *
 * The format of the file is a CSV file where each row has 3 sections. The first
 * element of a row is the logical id, which is an integer. The last element of
 * a row is a string that must match the filter string (so that means it's either
 * a p or a b character). Everything inbetween the first and last elements is an
 * integer index of a surface in the sheep mesh which is part of this panel. -1
 * may be given as an index and will be ignored.
 *
 * Something like:
 *
 * 43,73,p
 * 60,159,160,161,162,163,164,165,166,167,168,169,170,172,173,174,175,p
 *
 * Any row not conforming to the above should be safely ignored, so comments that
 * don't match that ordering shouldn't cause problems. Probably.
 */
TreeMap<Integer, ArrayList<Integer>> loadPolyMap(String labelFile, String sidePorB) {
  TreeMap<Integer, ArrayList<Integer>> polyMap = new TreeMap<Integer, ArrayList<Integer>>();  
  Table table = loadTable(labelFile);

  println(table.getRowCount() + " total rows in table"); 

  int cols = table.getColumnCount();
  ArrayList<Integer> rowInts = new ArrayList<Integer>();
  for (TableRow row : table.rows ()) {
    try {
      rowInts.clear();
      String last = null;
      
      for(int i=0; i<cols; i++) {
        last = row.getString(i);
        try {
          rowInts.add(Integer.parseInt(last));
        } catch (NumberFormatException nfe) {
          break;
        }
      }
      
      // Minimum number of elements for a row is 3
      if (rowInts.size() < 2) continue;
      if (sidePorB.equals(last)) {
        ArrayList<Integer> temp = new ArrayList<Integer>();
        int panel = rowInts.get(0);
  
        for(int i=1; i<rowInts.size(); i++) {
          temp.add(rowInts.get(i));
        }
  
        polyMap.put(panel, temp);
      }
    } catch (Exception ex) {
      println(ex);
    }
  }
  return polyMap;
}

/**
 * Both inverts the Z axis and scales the shape. The .obj uses a slightly
 * different coordinate system, hence the need for the inversion. The scaling
 * is for better font rendering on the labels.
 */
void invertShape(PShape shape) {
  if (shape==null) return;
  
  for(int i=0; i<shape.getVertexCount(); i++) {
    shape.setVertex(i, SHEEP_SCALE * shape.getVertexX(i), SHEEP_SCALE * shape.getVertexY(i), SHEEP_SCALE * -1 * shape.getVertexZ(i));
  }
}

/*******************************************************************************/
/*******************************************************************************/
/*******************************************************************************/

/**
 * The sheep holds the model and it's surfaces. It further provides access to
 * the Eyes.
 */
class Sheep {

  PShape sheepModel;
  PShape[] sheepPanelArray;
  
  PVector[] panelCenters;

  Eye leftEye;
  Eye rightEye;
  
  int panelCursor;
  boolean showLabels = false;
  boolean showLogicalHighlight = false;
  
  int logicalCursor = 1;

  public Sheep(PApplet app, String fileName) {
    sheepModel = loadShape(fileName); 

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

    // These are the same transforms that we baked into the sheep model. We
    // apply them again so that these direct text calls we are about to issue
    // will align with the sheep sides
    PMatrix3D matrix = new PMatrix3D();
    matrix.rotateX(PI);
    matrix.rotateY(PI*0.5);
    matrix.translate(SHEEP_SCALE * 30, SHEEP_SCALE * 10, SHEEP_SCALE * 550); // Shit, still in model coord space. Lame!
        
    panelCenters = new PVector[sheepPanelArray.length];
    for(int i=0; i<sheepPanelArray.length; i++) {
      PShape shape = sheepPanelArray[i];
      if (shape == null) {
        panelCenters[i] = new PVector(0.0f, 0.0f, 0.0f);
        continue;
      }
      // Must invert all shapes
      invertShape(shape);
      
      // Calculate the center by averaging all vertexes
      float x = 0.0f;
      float y = 0.0f;
      float z = 0.0f;
      
      int count = shape.getVertexCount();
      
      for(int j=0; j<count; j++) {
        x += shape.getVertexX(j);
        y += shape.getVertexY(j);
        z += shape.getVertexZ(j);
      }
      
      x = x / count;
      y = y / count;
      z = z / count;
      
      panelCenters[i] = matrix.mult(new PVector(x,y,z), null);
   
      
      // If it's an unmapped shape, make it dark
      if (!all.contains(i)) {
        shape.setFill(#303030);
      }
      
//      shape.setStroke(true);
      shape.setStroke(#303030);
      shape.setStrokeWeight(2f);
    }

    sheepModel.rotateY(PI*1.5);
    sheepModel.rotateZ(PI);
    //sheepModel.translate(SHEEP_SCALE * 30, SHEEP_SCALE * 10, SHEEP_SCALE * 550); // Shit, still in model coord space. Lame!
    sheepModel.translate(SHEEP_SCALE * 550, SHEEP_SCALE * 0, SHEEP_SCALE * 30); // Shit, still in model coord space. Lame!
    
    leftEye = new Eye(app, "Left eye", 400, 
      new PVector(SHEEP_SCALE * -135, SHEEP_SCALE * -215, SHEEP_SCALE * 27),
      22,  0, 160);
    rightEye = new Eye(app, "Right eye", 416, 
      new PVector(SHEEP_SCALE * -135, SHEEP_SCALE * -215, SHEEP_SCALE * -27), 
      -22, 150, 160);
    
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

        }
      }
    } else {
       System.out.println("Panel "+panel+" side="+side+" number was not found in map.  Bypassing command."); 
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
  
  public void moveLogicalCursor(int direction) {
    if (logicalCursor < 0) {
      logicalCursor = 1;
      return;
    }
    
    int max = partySideMap.lastKey();
    logicalCursor += direction;
    if (logicalCursor < 1) {
      logicalCursor += max;
    } else if (logicalCursor > max) {
      logicalCursor -= max;
    }      
  }
  
  void setShowLabels(boolean shouldDraw) {
    showLabels = shouldDraw;
    
    // Set all the surfaces to stroke
    for(PShape shape: sheepPanelArray) {
      if (shape==null) continue;
      
      shape.setStroke(showLabels);
      if (showLabels) {
        shape.setStroke(#303030);
        shape.setStrokeWeight(2f);
      }    
    }
  }
  
  /**
   * Set all of the panels (including non-mapped ones) to colors from a contrasting list.
   * This isn't pretty, but it lets you see where the panels are instead of just
   * the surfaces (which you can see with showLabels mode)
   */
  public void setContrastingColors() {
    int[] divColors = {
color(141,211,199),color(255,255,179),color(190,186,218),color(251,128,114),color(128,177,211),color(253,180,98),color(179,222,105),color(252,205,229),color(217,217,217),color(188,128,189),color(204,235,197),color(255,237,111)
    };
    
    int cIx = 0;
    for(Map.Entry e: partySideMap.entrySet()) {
      int logIx = (Integer)e.getKey();
      ArrayList<Integer> list;
      
      // First the party side
      list = (ArrayList<Integer>)e.getValue();
      for(int sIx: list) {
        try {
          PShape panel = sheepPanelArray[sIx];
          panel.setFill(divColors[cIx]);
        } catch (Exception ex) {
          // ignore
        }
      }
      
      // Then the bidness
      list = (ArrayList<Integer>)boringSideMap.get(logIx);
      if (list != null) {
        for(int sIx: list) {
          try {
            PShape panel = sheepPanelArray[sIx];
            panel.setFill(divColors[cIx]);
          } catch (Exception ex) {
            // ignore
          }
        }
      }
      
      cIx++;
      if (cIx == divColors.length) {
        cIx = 0;
      }
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
    
    // Logical panel cursor
    if (logicalCursor != -1 && showLogicalHighlight) {
      paintList(partySideMap.get(logicalCursor), true);
      paintList(boringSideMap.get(logicalCursor), false);
    }
    
    // For all panels, draw their logical name on the first element of them
    if (showLabels) {
      pushMatrix();
      
      fill(#ff0000);
      textAlign(CENTER, CENTER);
      textSize(14);
      
      drawLabels(true);
      drawLabels(false);
      
      popMatrix();
    }
    
 
    // This restores the matrix that was pushed at the beginning of 
    // this function.
    popMatrix();
  }
  
  void paintList(ArrayList<Integer> list, boolean isParty) {
    if (list==null) return;
    
    for(int i=0; i<list.size(); i++) {
      int surfaceIx = list.get(i);
      if (surfaceIx < 0 || surfaceIx > sheepPanelArray.length - 1) continue;
      
      PShape shape = sheepPanelArray[surfaceIx];
      if (shape == null) continue;
      
      shape.disableStyle();
      fill(isParty ? 0xFFFF0000 : 0xFF0000FF);
      shape(shape);
      shape.enableStyle();
    }
  }
  
  void drawLabels(boolean isParty) {
    
    colorMode(HSB, 255);

    StringBuffer buf = new StringBuffer();
    
    for(Map.Entry e: (isParty ? partySideMap.entrySet() : boringSideMap.entrySet()) ) {
      int logical = (Integer)e.getKey();
      ArrayList<Integer> list = (ArrayList<Integer>)e.getValue();
      if (list.size() < 1) continue;
      
      buf.setLength(0);
      buf.append(logical);
      buf.append(isParty ? "p" : "b");

      for(int j=0; j<list.size(); j++) {
        int sIx = list.get(j);
        
        if (j==0) {
          textSize(14);
        } else {
          textSize(8);
        }
       
        PVector center = panelCenters[sIx]; 
        if (center != null) {
          PShape shape = sheepPanelArray[sIx];
          if (shape!=null) {
            color fc = shape.getFill(0);
            float h = hue(fc) + 0.5f;
            if (h > 1.0f) h-=0.5f;
            color nc = color(255 * h, 255 * saturation(fc), 255 * brightness(fc));
            fill(nc);
          }
          
          float x = center.x;
          if (logical > 49 && logical < 60) {
            // Tail move right
            x += 20;
          } else if (logical > 60) {
            // Head move left
            x -= 20;
          } else if (logical > 0 && logical < 4) {
            // front shoulder region a little left
            x -= 10;
          } else if (logical > 31) {
            // Rump section, go right
            x += 20;
          }
          float z = center.z + (isParty ? 10 : -10);
          text(buf.toString(),  x, center.y, z);
        }
      }
    }  
   
    colorMode(RGB, 255); 
  }
  
  /*******************************************************************************/
  /*******************************************************************************/
  /*******************************************************************************/

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
    final float BEAM_LENGTH = SHEEP_SCALE * 5000;
    final float BEAM_MAX_SPOT = SHEEP_SCALE * 50;
    boolean nextIsPan;
    
    final int DMX_PAN = 3;
    final int DMX_PAN_FINE = 13;
    final int DMX_TILT = 4;
    final int DMX_TILT_FINE = 14;
    final int DMX_COLOR_WHEEL = 6;
    final int DMX_STROBE = 2;
    final int DMX_DIMMER = 1;
    final int DMX_GOBO = 7;
    final int DMX_EFFECT = 8;
    final int DMX_LADDER_PRISM = 10;
    final int DMX_8_FACET_PRISM = 0;
    final int DMX_3_FACET_PRISM = 0;
    final int DMX_FOCUS = 11;
    final int DMX_FROST = 12;
    final int DMX_PAN_TILT_SPEED = 5;
    final int DMX_RESET_AND_LAMP = 16;
    
    String me;
    PVector position;
    float offsetDegrees;
    Anchor anchor;

    GLabel lblColor;
    GLabel lblStrobe;
    GLabel lblGobo;
    GLabel lblEffect;
    GLabel lblLadder;
    GLabel lbl8Facet;
    GLabel lbl3Facet;
    GLabel lblFocus;
    GLabel lblFrost;
    GLabel lblPNTSpeed;
    GLabel lblReset;
    
    Eye(PApplet app, String me, int dmx, PVector position, float offsetDegrees, int labelX, int labelY) {
      this.me = me;
      this.dmxOffset = dmx;
      this.position = position;
      this.offsetDegrees = offsetDegrees;
      
      ///////
      // The labels for things we don't otherwise simulate visually
      final int LBL_HEIGHT=15;
      final int LBL_WIDTH = 150;
      final int ROW_HEIGHT = 20;
      int y = labelY;
      
      lblColor = new GLabel(app, labelX, y, LBL_WIDTH, LBL_HEIGHT, "color");
      y += ROW_HEIGHT;
      
      lblStrobe = new GLabel(app, labelX, y, LBL_WIDTH, 2*LBL_HEIGHT, "strobe");
      y += 2*ROW_HEIGHT;
 
      lblGobo = new GLabel(app, labelX, y, LBL_WIDTH, 2*LBL_HEIGHT, "gobo");
      y += 2*ROW_HEIGHT;

      lblEffect = new GLabel(app, labelX, y, LBL_WIDTH, LBL_HEIGHT, "effect");
      y += ROW_HEIGHT;

      lblLadder = new GLabel(app, labelX, y, LBL_WIDTH, LBL_HEIGHT, "ladder");
      y += ROW_HEIGHT;

      lbl8Facet = new GLabel(app, labelX, y, LBL_WIDTH, LBL_HEIGHT, "8 facet");
      y += ROW_HEIGHT;

      lbl3Facet = new GLabel(app, labelX, y, LBL_WIDTH, LBL_HEIGHT, "3 facet");
      y += ROW_HEIGHT;

      lblFocus = new GLabel(app, labelX, y, LBL_WIDTH, LBL_HEIGHT, "focus");
      y += ROW_HEIGHT;

      lblFrost = new GLabel(app, labelX, y, LBL_WIDTH, 2*LBL_HEIGHT, "frost");
      y += 2*ROW_HEIGHT;

      lblPNTSpeed = new GLabel(app, labelX, y, LBL_WIDTH, LBL_HEIGHT, "pnt speed");
      y += ROW_HEIGHT;

      lblReset = new GLabel(app, labelX, y, LBL_WIDTH, LBL_HEIGHT, "reset");
      y += ROW_HEIGHT;
      
      //////
      watch = new StopWatch();
      
      anchor = new Anchor(app);
      
      cone = new Cone(app, 40, new PVector(0, 1, 0), new PVector(0, BEAM_LENGTH, 0));
      cone.setSize(BEAM_MAX_SPOT, BEAM_MAX_SPOT, BEAM_LENGTH);
      cone.fill(0x80ffff00);
      cone.drawMode(Shape3D.SOLID);
      
      anchor.addShape(cone);
      
      anchor.moveTo(position);
//      cone.moveTo(position);
      
      anchor.rotateToY(radians(offsetDegrees));
//      cone.rotateToY(radians(offsetDegrees));
      
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
      
      anchor.draw();
//      cone.draw();

    }
    
    // Don't have exact specs so from Sharpy we get max speed pan 2.45s, tilt 1.30s 
    // For Super sharpy PAN fast = 3.301s, normal = 4.038s
    //                  TILT fast = 2.060, normal = 2.274s
    // Call it 3 s for max pan, and 1.8s for max tilt. Really should measure I guess... 
    final int MAX_PAN_PER_SECOND = (int)((float)0x0000ffff / 4.0f);
    final int MAX_TILT_PER_SECOND = (int)((float)0x0000ffff / 3.0f);
//    final int MAX_PAN_PER_SECOND = 0x00ffffff;
//    final int MAX_TILT_PER_SECOND = 0x00ffffff; 
    
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
      
      updateLabels();
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
      
      // Handle dimmer. We had this other code for pre-multiplying the dimmer
      // value into the color, but honestly this alpha channel stuff works
      // well and probably better.
      int brightness = channelValues[DMX_DIMMER] & 0x00ff;
//      int r = ( ((clr & 0x00ff0000) >> 16) * brightness ) >> 8;
//      int g = ( ((clr & 0x0000ff00) >>  8) * brightness ) >> 8;
//      int b = ( ((clr & 0x000000ff)      ) * brightness ) >> 8;
//      
//      clr = ((r << 16) & 0x00ff0000) | 
//            ((g <<  8) & 0x0000ff00) |
//            ((b      ) & 0x000000ff) |
//            0xc0000000;

      // strobe closed, make like 0, otherwise let it be what it is.
      if (channelValues[DMX_STROBE] <= 31) {
        brightness = 0;
      }


      clr = ((brightness << 24 ) & 0xff000000) | (clr & 0x00ffffff);
      cone.fill(clr, Cone.ALL);
      
      currentValues[DMX_COLOR_WHEEL] = c;
    }

    private void pad10(StringBuffer sb, int val) {
      if (val < 10) {
        sb.append(" ");
      }
      
      sb.append(val);
    }
    
    private void pad100(StringBuffer sb, int val) {
      if (val < 100) {
        sb.append(" ");
      }
      pad10(sb, val);
    }
    
    private void goboShake(StringBuffer sb, int val) {
      sb.append("SHK ");
      sb.append(val);
      sb.append(" of 5 S2F");
    }

    private void prism(StringBuffer sb, int v, String name) {      
      pad100(sb, v);
      if (v<=63) {
        sb.append(" ");
        sb.append(name);
        sb.append(" no func");
      } else if (v>=64 && v<=127) {       
        sb.append(" ");
        sb.append(name);
        sb.append(" slow rotate");
        v -= 64;
        pad10(sb, v);
        sb.append(" of 63 ??");
      } else if (v>=128 && v<=189) {       
        sb.append(" ");
        sb.append(name);
        sb.append(" FW ");
        v -= 128;
        pad10(sb, v);
        sb.append(" of 61 F2S");
      } else if (v>=190 && v<=193) {       
        sb.append(" ");
        sb.append(name);
        sb.append(" no rot");
      } else if (v>=194) {       
        sb.append(" ");
        sb.append(name);
        sb.append(" RV ");
        v -= 194;
        pad10(sb, v);
        sb.append(" of 61 S2F");
      }
    }      
    
    /**
     * Update all the text labels for the light features we don't handle
     */
    private void updateLabels() {
      StringBuffer sb = new StringBuffer();
      
      /// Color (particularly for rotation)
      int v = channelValues[DMX_COLOR_WHEEL];
      pad100(sb, v);
      if (v>=128 && v<=189) {
        sb.append(" FW ");
        v -= 128;
        pad10(sb, v);
        sb.append(" of 61 F2S");
      } else if (v>=190 && v<=192) {
        sb.append(" No Func");
      } else if (v>=194) {
        sb.append(" RV ");
        v -= 194;
        pad10(sb, v);
        sb.append(" of 61 S2F");
      }
      lblColor.setText(sb.toString());

      // Strobe
      sb.setLength(0);
      v = channelValues[DMX_STROBE];
      pad100(sb, v);
      if (v<=31) {
        sb.append(" closed");
      } else if ((v>=32 && v<=63) || (v>=96 && v<=127) || (v>=160 && v<=191) || (v>=224)) {
        sb.append(" open");
      } else if (v>=64 && v<=95) {       
        sb.append(" Strobe ");
        v -= 64;
        pad10(sb, v);
        sb.append(" of 31 S2F");
      } else if (v>=128 && v<=159) {       
        sb.append(" Pulse ");
        v -= 128;
        pad10(sb, v);
        sb.append(" of 31 S2F?");
      } else if (v>=192 && v<=223) {       
        sb.append(" Random ");
        v -= 192;
        pad10(sb, v);
        sb.append(" of 31 S2F");
      }
      lblStrobe.setText(sb.toString());
      
      // Gobo
      sb.setLength(0);
      v = channelValues[DMX_GOBO];
      pad100(sb, v);
      if (v<=6) {
        sb.append(" no gobo");
      } else if (v>=7 && v<=13) {       
        sb.append(" Circle 0 ");
      } else if (v>=14 && v<=20) {       
        sb.append(" Circle 1 ");
      } else if (v>=21 && v<=27) {       
        sb.append(" Circle 2 ");
      } else if (v>=28 && v<=34) {       
        sb.append(" Circle 3 ");
      } else if (v>=35 && v<=41) {       
        sb.append(" Circle 4 ");
      } else if (v>=42 && v<=48) {       
        sb.append(" Curve ");
      } else if (v>=49 && v<=55) {       
        sb.append(" 5 Stars ");
      } else if (v>=56 && v<=62) {       
        sb.append(" Star Curve ");
      } else if (v>=63 && v<=69) {       
        sb.append(" Circle Swoosh ");
      } else if (v>=70 && v<=76) {       
        sb.append(" Small Splat ");
      } else if (v>=77 && v<=83) {       
        sb.append(" Hairy Circle ");
      } else if (v>=84 && v<=90) {       
        sb.append(" Flower ");
      } else if (v>=91 && v<=97) {       
        sb.append(" Sperm ");
      } else if (v>=98 && v<=104) {       
        sb.append(" Ying Yang ");
      } else if (v>=105 && v<=111) {       
        sb.append(" Lightning ");
      } else if (v>=112 && v<=119) {       
        sb.append(" Big Splat ");
      } else if (v>=120 && v<=125) {       
        sb.append(" Circle 0 ");
        v -= 120;
        goboShake(sb, v);
      } else if (v>=126 && v<=131) {       
        sb.append(" Circle 1 ");
        v -= 126;
        goboShake(sb, v);
      } else if (v>=132 && v<=137) {       
        sb.append(" Circle 2 ");
        v -= 132;
        goboShake(sb, v);
      } else if (v>=138 && v<=143) {       
        sb.append(" Circle 3 ");
        v -= 138;
        goboShake(sb, v);
      } else if (v>=144 && v<=149) {       
        sb.append(" Circle 4 ");
        v -= 144;
        goboShake(sb, v);
      } else if (v>=150 && v<=155) {       
        sb.append(" Curve ");
        v -= 150;
        goboShake(sb, v);
      } else if (v>=156 && v<=161) {       
        sb.append(" 5 Stars ");
        v -= 156;
        goboShake(sb, v);
      } else if (v>=162 && v<=167) {       
        sb.append(" Star Curve ");
        v -= 162;
        goboShake(sb, v);
      } else if (v>=168 && v<=173) {       
        sb.append(" Circle Swoosh ");
        v -= 168;
        goboShake(sb, v);
      } else if (v>=174 && v<=179) {       
        sb.append(" Small Splat ");
        v -= 174;
        goboShake(sb, v);
      } else if (v>=180 && v<=185) {       
        sb.append(" Hairy Circle ");
        v -= 180;
        goboShake(sb, v);
      } else if (v>=186 && v<=191) {       
        sb.append(" Flower ");
        v -= 186;
        goboShake(sb, v);
      } else if (v>=192 && v<=197) {       
        sb.append(" Sperm ");
        v -= 192;
        goboShake(sb, v);
      } else if (v>=198 && v<=203) {       
        sb.append(" Ying Yang ");
        v -= 198;
        goboShake(sb, v);
      } else if (v>=204 && v<=209) {       
        sb.append(" Lightning ");
        v -= 204;
        goboShake(sb, v);
      } else if (v>=210 && v<=217) {       
        sb.append(" Big Splat ");
        v -= 210;
        goboShake(sb, v);
        
      } else if (v>=218) {
        sb.append(" Rot ");
        v -= 218;
        pad10(sb, v);
        sb.append(" of 37 S2F");
      }
      lblGobo.setText(sb.toString());
      
      
      // Effect
      sb.setLength(0);
      v = channelValues[DMX_EFFECT];
      pad100(sb, v);
      if (v<=64) {
        sb.append(" no effect");
      } else if (v>=65 && v<=128) {       
        sb.append(" Ladder");
      } else if (v>=129 && v<=191) {       
        sb.append(" 8 Facet");
      } else if (v>=192) {       
        sb.append(" 3 Facet");
      }
      lblEffect.setText(sb.toString());


      // Ladder
      sb.setLength(0);
      v = channelValues[DMX_LADDER_PRISM];
      prism(sb, v, "LP");
      lblLadder.setText(sb.toString());
            

      // 8 Facet
      sb.setLength(0);
      v = channelValues[DMX_8_FACET_PRISM];
      prism(sb, v, "8F");
      lbl8Facet.setText(sb.toString());


      // Ladder
      sb.setLength(0);
      v = channelValues[DMX_3_FACET_PRISM];
      prism(sb, v, "3F");
      lbl3Facet.setText(sb.toString());
      
      
      // Focus
      sb.setLength(0);
      v = channelValues[DMX_FOCUS];
      pad100(sb,v);
      sb.append(" of 255 focus");
      lblFocus.setText(sb.toString());
      
     
      // Frost
      sb.setLength(0);
      v = channelValues[DMX_FROST];
      pad100(sb, v);
      if (v<=191) {
        sb.append(" of 191 Steady Frost");
      } else if (v>=192 && v<=223) {
        sb.append(" Pulse Open ");
        v -= 192;
        pad10(sb,v);
        sb.append(" of 31 F2S");
      } else if (v>=224 && v<=254) {
        sb.append(" Pulse Close ");
        v -= 224;
        pad10(sb,v);
        sb.append(" of 30 F2S");
      } else if (v==255) {       
        sb.append("Max Frost");
      }
      lblFrost.setText(sb.toString());
      
      
      // PNT Speed
      sb.setLength(0);
      v = channelValues[DMX_PAN_TILT_SPEED];
      pad100(sb,v);
      if (v<=225) {
        sb.append(" of 225 Max to min");
      } else {
        sb.append(" no func");
      }
      lblPNTSpeed.setText(sb.toString());
      
      // Reset
      sb.setLength(0);
      v = channelValues[DMX_RESET_AND_LAMP];
      pad100(sb,v);
      if (v<=39) {
        sb.append(" no reset func");
      } else if (v>=40 && v<=59) {
        sb.append(" lamp on");
      } else if (v>=60 && v<=79) {
        sb.append(" lamp off");
      } else if (v>=80 && v<=84) {
        sb.append(" reset");
      } else {
        sb.append(" no func");
      }
      lblReset.setText(sb.toString());

      
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