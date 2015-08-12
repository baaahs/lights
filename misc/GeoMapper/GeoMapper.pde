import java.util.*;

//import shapes3d.*;
//import shapes3d.animation.*;
import g4p_controls.*;


final int WINDOW_WIDTH  = 1200;
final int WINDOW_HEIGHT =  800;

//Whole Object representation.
Sheep theSheep;
TreeMap<Integer, ArrayList<Integer>> partySideMap = new TreeMap<Integer, ArrayList<Integer>>();
TreeMap<Integer, ArrayList<Integer>> boringSideMap = new TreeMap<Integer, ArrayList<Integer>>();


// This scale is applied to the loaded OBJ and then everything else that
// was originally scaled relative to the baseline OBJ. The issue was that
// at the original scale, all the font sizes were tiny, and apparently they
// get prerendered to surfaces because they came out extra fuzzy and crappy.
// Scaling everything up seems to have resolved that.

final int SHEEP_SCALE = 3;

final float ANAL_FOV = PI / 18; // 10 degrees

final float PAN_STEPS = (TWO_PI) / ANAL_FOV;
final float TILT_STEPS = PAN_STEPS / 2;

GButton btnPrevious;
GButton btnNext;

GCheckbox cbAnalysisCamera;

Camera camera;
Camera analysisCamera;

// setup() is called once by the environment to initialize things
void setup() {
  size(WINDOW_WIDTH, WINDOW_HEIGHT, P3D);
  
  // Some UI stuff. Need to get G4P up and running before PeasyCam
  G4P.setGlobalColorScheme(G4P.YELLOW_SCHEME);
  btnPrevious = new GButton(this, 5, 5, 70, 15, "Previous");
  btnNext = new GButton(this, 80, 5, 50, 15, "Next");
  
  cbAnalysisCamera = new GCheckbox(this, 5, 25, 300, 15, "Analysis Camera");

  // Initialize camera movements
  camera = new Camera(this, 0, SHEEP_SCALE * -300, SHEEP_SCALE * 500);
  
  analysisCamera = new Camera(this, 
    0, 0, 0,   // location
   -100, 0, 0,  // target
    ANAL_FOV, 1.0, 1, 1000 // fOV, aspect, near clip, far clip
    );
  
  // Load the .csv file which contains a mapping from logical panel
  // numbers used by the shows (and by the construction documents) into
  // surface indexes for the 3D model. Some panels map to up to 3 
  // surfaces (i.e. it's not strictly 1 to 1). The file is loaded twice,
  // once for each side.
  partySideMap = loadPolyMap("../../SheepSimulator/SheepPanelPolyMap.csv", "p");
  boringSideMap = loadPolyMap("../../SheepSimulator/SheepPanelPolyMap.csv", "b");

  // Most of the fun will happen in the sheep class, at least as far as 
  // display management goes.
  theSheep =  new Sheep(this, "../../../SheepSimulator/data/model.obj");
  
  // Will use the ground when drawing. It is just a really big rectangle
//  ground = createShape();
//  ground.beginShape();
//  ground.fill(#241906);
//  ground.vertex(SHEEP_SCALE * -10000,0,SHEEP_SCALE * -10000);
//  ground.vertex(SHEEP_SCALE * 10000,0,SHEEP_SCALE * -10000);
//  ground.vertex(SHEEP_SCALE * 10000,0,SHEEP_SCALE * 10000);
//  ground.vertex(SHEEP_SCALE * -10000,0,SHEEP_SCALE * 10000);
//  ground.endShape(CLOSE);
  
  // let's start with contrasting colors because they are prettier
  theSheep.setContrastingColors();

}


// Returns the number of non-black pixels seen by the current analysis camera view.
// It assumes the background is black and all panels that are desired are lit to non-black
int countPixels(String name) {
  
//  println("Counting pixels....");
  PGraphics pg = createGraphics(100, 100, P3D);
  
  pg.beginDraw();
  pg.background(0);
  
  analysisCamera.feedGraphics(pg);
  
  theSheep.drawLogicalCursor(pg);
  
  pg.endDraw();
  
  // Now count pixels
  pg.loadPixels();
  int len = pg.pixels.length;
  int count = 0;
  for(int i=0; i<len; i++) {  
    if ((pg.pixels[i] & 0x00ffffff) != 0) {
      count++;
    }
  }
  if (count > 0 && name != null) {
    pg.save(name);
  }
  
  return count;
}

class SectorId implements Comparable {
  float pan;
  float tilt;
  
  SectorId(float pan, float tilt) {
    this.pan = pan;
    this.tilt = tilt;
  }
  
  public int hashcode() {
    return (int)(pan * 1000 + tilt * 1000);
  }
  
  public boolean equals(Object obj) {
    if (!(obj instanceof SectorId)) return false;
    
    SectorId other = (SectorId)obj;
    return other.pan == this.pan && other.tilt == this.tilt;
  }
  
  public int compareTo(Object obj) {
    if (!(obj instanceof SectorId)) return -1;
    
    SectorId other = (SectorId)obj;

    
    if (this.pan < other.pan) {
      return -1;
    }
    if (this.pan > other.pan) {
      return 1;
    }
    
    // Pan is same, so how about tilt?
    if (this.tilt < other.tilt) {
      return -1;
    }
    if (this.tilt > other.tilt) {
      return 1;
    }
    
    // Samsies
    return 0;
  }
  
}


class PixelCount extends SectorId{
  int count;
  String panelName;
  
  float percentOfTotalPanel;
  
  PixelCount(float pan, float tilt, int count, String panelName) {
    super(pan, tilt);
    
    this.count = count;    
    this.panelName = panelName;
  }  
}



// For a given panel, iterate through all positions of pan and tilt, returning PixelCount
// objects for locations that have a count.
ArrayList<PixelCount> analyzePanel(int num, boolean isParty) {
  theSheep.setLogicalCursor(num, isParty);
  
  
  String pName = Integer.toString(num)+(isParty?"p":"b");
  StringBuffer sb = new StringBuffer();
  println("Analyzing "+pName+"  tilt steps="+TILT_STEPS);
  
  ArrayList<PixelCount> list = new ArrayList<PixelCount>();
  for(int tiltIx=0; tiltIx<TILT_STEPS; tiltIx++) {
    for(int panIx=0; panIx<PAN_STEPS; panIx++) {
      analysisCamera.aim(-100, 0, 0);
      analysisCamera.tilt(HALF_PI);
      
      float pan = panIx * -ANAL_FOV;
      float tilt = tiltIx * -ANAL_FOV;
      analysisCamera.pan(pan);
      analysisCamera.tilt(tilt);      
    
      int count = countPixels(null);
      
      if (count > 0) {
        list.add(new PixelCount(pan, tilt, count, pName));
      }
    }
  } 
  
  return list;
}

class VisualSector {
  SectorId id;
  
  HashMap<String, PixelCount> countPerPanel = new HashMap<String, PixelCount>();
  
  VisualSector(SectorId id) {
    this.id = new SectorId(id.pan, id.tilt);
  }
}

void addToSector(Map<SectorId, VisualSector> sectors, ArrayList<PixelCount> counts) {
  int totalPixels = 0;
  
  for(PixelCount count: counts) {
    // count is a sub class of SectorId remember
    VisualSector sector = sectors.get(count);
    
    if (sector == null) {
      sector = new VisualSector(count);
      sectors.put(count, sector);
    }
    
    sector.countPerPanel.put(count.panelName, count);
    totalPixels += count.count;
  }
  
  // Now again to update all the percentages
  for(PixelCount count: counts) {
    count.percentOfTotalPanel = (float)count.count/(float)totalPixels;
  }
}

void analyzeAll() {
  TreeMap<SectorId, VisualSector> sectors = new TreeMap<SectorId, VisualSector>();
  
  // Iterate through all panels
//  int toDo = 5;
  for(int panelNum: partySideMap.keySet()) {
    ArrayList<PixelCount> counts = analyzePanel(panelNum, true);
    addToSector(sectors, counts);
    
//    toDo--;
//    if (toDo == 0) break;
  }

  for(int panelNum: boringSideMap.keySet()) {
    ArrayList<PixelCount> counts = analyzePanel(panelNum, false);
    addToSector(sectors, counts);
  }
  
  println("Writing to sectors.json");
  // Output one big ole JSON love fest of goodness
  PrintWriter output = createWriter("sectors.json");
  output.println("[");
  
  
  for(int panIx=0; panIx<PAN_STEPS; panIx++) {
    if (panIx == 0) {
      output.println("    [");
    } else {
      output.println("  , [");
    }
    
    for(int tiltIx=0; tiltIx<TILT_STEPS; tiltIx++) {
      float pan = panIx * -ANAL_FOV;
      float tilt = tiltIx * -ANAL_FOV;

      SectorId id = new SectorId(pan, tilt);
      
      VisualSector sector = sectors.get(id);
      printSector(output, tiltIx==0, id, sector);
    }
    
    output.println("  ]");
    output.println();
  }

  output.flush();
  output.close();
  println("output finished");
}

void printSector(PrintWriter output, boolean isFirstSector, SectorId id, VisualSector sector) {

  
  
  if (isFirstSector) {
    output.print("      ");
  } else {
    output.print("    , ");
  }

  output.print("{ \"_pan\":");
  output.print(id.pan);
  output.print(", \"_tilt\":");
  output.print(id.tilt);
  
  if (sector != null) {    
    for(String panelName: sector.countPerPanel.keySet()) {
      output.print(", ");        

      output.print("\"");
      output.print(panelName);
      output.print("\":");
      output.print(sector.countPerPanel.get(panelName).percentOfTotalPanel);
    }
  }
  output.println("}");
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
  
  if (cbAnalysisCamera.isSelected()) {
    analysisCamera.feed();
  } else {
    camera.feed();
  }
  
  // Draw the sheep surfaces in their current colors etc.
  theSheep.draw();
  
//  shape(ground);
  
  // Also draw a center axis for general 3d reference. Red in +X axis,
  // Green in +Y, and Blue in +Z
  stroke(#ff0000);
  line(0, 0, 0, SHEEP_SCALE * 10, 0, 0);
  stroke(#00ff00);
  line(0, 0, 0, 0, SHEEP_SCALE * 10, 0);
  stroke(#0000ff);
  line(0, 0, 0, 0, 0, SHEEP_SCALE * 10);
 
  popMatrix();
  
  // Reset the camera for the UI elements
  perspective();
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

void keyPressed() {
  if (!cbAnalysisCamera.isSelected()) {
    return;
  }
  
//  if (key == CODED) {
    switch(keyCode) {
      case UP:
        analysisCamera.tilt(ANAL_FOV);
        break;
        
      case DOWN:
        analysisCamera.tilt(-ANAL_FOV);
        break;
     
      case LEFT:
        analysisCamera.pan(-ANAL_FOV);
        break;
        
      case RIGHT:
        analysisCamera.pan(ANAL_FOV);
        break;
    }
//  }
}

void keyTyped() {
  println("typed "+key);
  
  switch(key) {
    // The logical cursor
    case ']': // Next
      theSheep.moveLogicalCursor(1);
      break;
      
    case '}': // Next
      theSheep.moveLogicalCursor(10);
      break;
      
    case '[': // Prev
      theSheep.moveLogicalCursor(-1);
      break;
      
    case '{': // Prev
      theSheep.moveLogicalCursor(-10);
      break;

    case 'c':
      int count = countPixels("manual.png");
      println(""+count+" pixels");
      break;

    case 'a':
      ArrayList<PixelCount> list = analyzePanel(theSheep.logicalCursor, true);
      println(list);
      break;

    case 'b':
      ArrayList<PixelCount> listB = analyzePanel(theSheep.logicalCursor, false);
      println(listB);
      break;
      
    case 'l':
      analyzeAll();
      break;
  }
}

/**
 * Handle events from GButton buttons. Mostly we reset the display
 */
void handleButtonEvents(GButton button, GEvent event) {
  if (button == btnPrevious) {
  } else if(button == btnNext) {
//    camera.jump(SHEEP_SCALE * 500, SHEEP_SCALE * -60, SHEEP_SCALE * 400);
//    camera.aim(0,SHEEP_SCALE * -100,0);
  }
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
 
  boolean showLogicalHighlight = false;  
  public int logicalCursor = 1;
  public boolean logicalParty = true;

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
    PVector translation = new PVector(SHEEP_SCALE * 30, SHEEP_SCALE * -100, SHEEP_SCALE * 500);
    matrix.translate(translation.x, translation.y, translation.z);
        
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

    sheepModel.rotateX(PI);
    sheepModel.rotateY(PI*0.5);
    sheepModel.translate(translation.x, translation.y, translation.z); // Shit, still in model coord space. Lame!
    
//    leftEye = new Eye(app, "Left eye", 400, new PVector(SHEEP_SCALE * -135, SHEEP_SCALE * -215, SHEEP_SCALE * 27), 35);
//    rightEye = new Eye(app, "Right eye", 416, new PVector(SHEEP_SCALE * -135, SHEEP_SCALE * -215, SHEEP_SCALE * -27), -22);
    
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
       System.out.println("Panel number was not found in map.  Bypassing command."); 
    }
  } // end setPanelColor
  
//  public void moveCursor(int direction) {
//    int prev = panelCursor;
//    
//    panelCursor += direction;
//    if (panelCursor >= sheepPanelArray.length) {
//      panelCursor -= sheepPanelArray.length;
//    } else if (panelCursor < 0) {
//      panelCursor += sheepPanelArray.length;
//    }        
//  }
//  
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
  
//  void setShowLabels(boolean shouldDraw) {
//    showLabels = shouldDraw;
//    
//    // Set all the surfaces to stroke
//    for(PShape shape: sheepPanelArray) {
//      if (shape==null) continue;
//      
//      shape.setStroke(showLabels);
//      if (showLabels) {
//        shape.setStroke(#303030);
//        shape.setStrokeWeight(2f);
//      }    
//    }
//  }
  
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
//    leftEye.draw();
//    rightEye.draw();
    
    // Finally (for the sheep at least) we re-render one surface
    // in a different color. Do this by re-rendering rather than 
    // changing the style so that we don't loose the style for this
    // surface just because the cursor traversed it.
//    PShape curPanel = sheepPanelArray[panelCursor];
//    if (curPanel != null) {
//      sheepPanelArray[panelCursor].disableStyle(); 
//      fill(0xff00ff00);
//      shape(sheepPanelArray[panelCursor]);
//      sheepPanelArray[panelCursor].enableStyle(); 
//    }
    
    // Logical panel cursor
    if (logicalCursor != -1) {
      paintList(partySideMap.get(logicalCursor), true);
      paintList(boringSideMap.get(logicalCursor), false);
    }
    
    // This restores the matrix that was pushed at the beginning of 
    // this function.
    popMatrix();
  }
  
  public void drawLogicalCursor(PGraphics pg) {
    if (logicalCursor != -1) {
      ArrayList<Integer> list = null;
      if (logicalParty) {
        list = partySideMap.get(logicalCursor);
      } else {
        list = boringSideMap.get(logicalCursor);
      }
      
      if (list == null) {
        return;
      }
      
      for(int i=0; i<list.size(); i++) {
        int surfaceIx = list.get(i);
        if (surfaceIx < 0 || surfaceIx > sheepPanelArray.length - 1) continue;
        
        PShape shape = sheepPanelArray[surfaceIx];
        if (shape == null) continue;
        
        shape.disableStyle();
        pg.fill(0xffffffff);
        pg.shape(shape);
        shape.enableStyle();
      }
      
    }
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
  
  void setLogicalCursor(int val, boolean isParty) {
    this.logicalParty = isParty;
    this.logicalCursor = val;
  }
}

