
# Some basic facts about the Quadron
SHORT_SIDE = 36
LONG_SIDE = 60

class Edge(object):
    def __init__(self, channel, sheep_num, sheep_side, is_forward, is_long=False):
        self.channel = channel
        self.is_forward = is_forward
        self.is_long = is_long

        # Make the fade candy total universe pixel offsets
        start = channel * 64
        self.num_pixels = SHORT_SIDE
        if is_long:
            self.num_pixels = LONG_SIDE

        end = start + self.num_pixels
        step = 1

        if not is_forward:
            start, end = end, start
            step = -1

        self.pixels = []
        for ix in range(start, end, step):
            self.pixels.append(ix)
        #

        # Come up with the sheep cell_ids based on our sheep number and side
        # Just separate everything by 64 because that's easy to remember and
        # easily includes the longest side
        sheep_offset = ((sheep_num-1) * 64) + 1
        self.sheep_side = sheep_side
        self.cell_ids = []
        self.panel_nums = []
        self.mapping = {}
        for ix in range(0,self.num_pixels):
            panel_num = sheep_offset + ix
            self.panel_nums.append(panel_num)
            cell_id = str(panel_num) + self.sheep_side
            self.cell_ids.append(cell_id)
            self.mapping[cell_id] = self.pixels[ix]


    def __repr__(self):
        return "Edge({})".format(self.cell_ids)


    def mapping_list(self):
        """
        Returns a list of tuples of (cell_id, pixel) that are the mappings
        from sheep space to fade candy pixel index
        """
        out = []
        for cell in self.cell_ids:
            out.append( (cell, self.mapping[cell]) )

        return out



class CompositeEdge(object):
    def __init__(self, edges):
        self.edges = edges
        self.consolidate()

    def __repr__(self):
        return "CompositeEdge({})".format(self.edges)

    @classmethod
    def using(cls, *names):
        out = cls([])
        for name in names:
            # print("Adding {}").format(name)
            out.edges.append(edges[name])

        out.consolidate()
        return out

    def consolidate(self):
        self.sheep_side = 'a'
        self.pixels = []
        self.panel_nums = []
        self.cell_ids = []
        self.mapping = {}
        for edge in self.edges:
            self.pixels += edge.pixels
            self.panel_nums += edge.panel_nums
            self.cell_ids += edge.cell_ids
            self.mapping.update(edge.mapping)

        self.num_pixels = len(self.pixels)
        # print("Num pixels = {}").format(self.num_pixels)

    def mapping_list(self):
        """
        Returns a list of tuples of (cell_id, pixel) that are the mappings
        from sheep space to fade candy pixel index
        """
        out = []
        for cell in self.cell_ids:
            out.append( (cell, self.mapping[cell]) )

        return out



# Start with our most basic edges 
base_edges = {
    "BOTTOM_REAR_LEFT":   Edge( 0, 1, "p", False),        # Rev
    "BOTTOM_FRONT_LEFT":  Edge( 1, 2, "p",  True),        # Forward
    "BOTTOM_LEFT_LS":     Edge( 2, 3, "p",  True, True),  # Forward
    "BOTTOM_FRONT_RIGHT": Edge( 3, 2, "b",  True),        # rev
    # 4 = nothing
    "BOTTOM_REAR_RIGHT":  Edge(12, 1, "b", False),        # Forward
    "BOTTOM_RIGHT_LS":    Edge( 5, 3, "b", False, True),  # Forward
    "TOP_REAR_LEFT":      Edge( 6, 4, "p", False),        # Rev
    "TOP_REAR_MIDDLE":    Edge( 7, 5, "p", False),        # Rev
    "TOP_REAR_RIGHT":     Edge( 8, 6, "p",  True),        # Forward
    "TOP_FRONT_RIGHT":    Edge(10, 6, "b",  True),        # Rev
    "TOP_FRONT_MIDDLE":   Edge(11, 5, "b",  True),        # Rev
    "TOP_FRONT_LEFT":     Edge( 9, 4, "b", False),        # Forward
}

edges = base_edges.copy()

# Now add the Composite edges
faces = {
    "BOTTOM_LEFT_ALL": CompositeEdge.using("BOTTOM_REAR_LEFT", "BOTTOM_FRONT_LEFT", "BOTTOM_LEFT_LS"),
    "BOTTOM_RIGHT_ALL": CompositeEdge.using("BOTTOM_FRONT_RIGHT", "BOTTOM_REAR_RIGHT", "BOTTOM_RIGHT_LS"),
    "TOP_REAR_ALL": CompositeEdge.using("TOP_REAR_LEFT", "TOP_REAR_MIDDLE", "TOP_REAR_RIGHT"),
    "TOP_FRONT_ALL": CompositeEdge.using("TOP_FRONT_RIGHT", "TOP_FRONT_MIDDLE", "TOP_FRONT_LEFT"),
}
edges.update(faces)

all_edges = CompositeEdge(base_edges.values())

party = CompositeEdge.using("BOTTOM_LEFT_ALL","TOP_REAR_ALL")
business = CompositeEdge.using("BOTTOM_RIGHT_ALL", "TOP_FRONT_ALL")

##############
# Historically animations looked for "panel numbers" which are shared between
# party and business side. The sheep_side objects then append a side indicator
# to those numbers.

ALL = party.panel_nums

# Some interesting slices
by_edges = map(lambda edge: edge.cell_ids, base_edges.values())
by_faces = map(lambda edge: edge.cell_ids, faces.values())

# Moving perpendicular to the long axis, sliced into planes
by_long_planes = []
side_ix = 0
for ix in range(0,60):
    plane = []
    by_long_planes.append(plane)

    plane.append(edges["BOTTOM_LEFT_LS"].cell_ids[59-ix])
    plane.append(edges["BOTTOM_RIGHT_LS"].cell_ids[59-ix])

    reverse_side_ix = 35-side_ix
    trix = side_ix
    trix_inc = 1
    tlix = side_ix
    tlix_inc = 1

    if ix < 30:
        fr = "REAR"
        trix = reverse_side_ix
        trix_inc = -1
    else:
        fr = "FRONT"
        tlix = reverse_side_ix
        tlix_inc = -1


    plane.append(edges["TOP_"+fr+"_LEFT"].cell_ids[tlix])
    plane.append(edges["TOP_"+fr+"_RIGHT"].cell_ids[trix])
    plane.append(edges["BOTTOM_"+fr+"_LEFT"].cell_ids[side_ix])
    plane.append(edges["BOTTOM_"+fr+"_RIGHT"].cell_ids[side_ix])
    side_ix += 1
    trix += trix_inc
    tlix += tlix_inc

    if ix % 5 == 0:
        plane.append(edges["TOP_"+fr+"_LEFT"].cell_ids[tlix])
        plane.append(edges["TOP_"+fr+"_RIGHT"].cell_ids[trix])
        plane.append(edges["BOTTOM_"+fr+"_LEFT"].cell_ids[side_ix])
        plane.append(edges["BOTTOM_"+fr+"_RIGHT"].cell_ids[side_ix])
        side_ix += 1


    if ix == 29:
        plane.extend(edges["TOP_REAR_MIDDLE"].cell_ids)
        side_ix = 0 

    if ix == 30:
        plane.extend(edges["TOP_FRONT_MIDDLE"].cell_ids)


by_short_planes = []
side_ix = 0
for ix in range(0,36):
    plane = []
    by_short_planes.append(plane)

    plane.append(edges["TOP_REAR_MIDDLE"].cell_ids[35-ix])
    plane.append(edges["TOP_FRONT_MIDDLE"].cell_ids[35-ix])

    reverse_side_ix = 35-side_ix
    brix = side_ix
    brix_inc = 1
    bfix = side_ix
    bfix_inc = 1

    if ix < 18:
        lr = "RIGHT"
        brix = reverse_side_ix
        brix_inc = -1
    else:
        lr = "LEFT"
        bfix = reverse_side_ix
        bfix_inc = -1


    plane.append(edges["TOP_REAR_"+lr].cell_ids[side_ix])
    plane.append(edges["TOP_FRONT_"+lr].cell_ids[side_ix])
    plane.append(edges["BOTTOM_REAR_"+lr].cell_ids[brix])
    plane.append(edges["BOTTOM_FRONT_"+lr].cell_ids[bfix])
    side_ix += 1
    brix += brix_inc
    bfix += bfix_inc


    plane.append(edges["TOP_REAR_"+lr].cell_ids[side_ix])
    plane.append(edges["TOP_FRONT_"+lr].cell_ids[side_ix])
    plane.append(edges["BOTTOM_REAR_"+lr].cell_ids[brix])
    plane.append(edges["BOTTOM_FRONT_"+lr].cell_ids[bfix])
    side_ix += 1

    if ix == 17:
        plane.extend(edges["BOTTOM_RIGHT_LS"].cell_ids)
        side_ix = 0

    if ix == 18:
        plane.extend(edges["BOTTOM_LEFT_LS"].cell_ids)

###########
if __name__=='__main__':
    # print edges

    all_mappings = []
    for name, edge in base_edges.iteritems():
        print "[{}]".format(name)

        lst = edge.mapping_list()
        print lst
        all_mappings += lst
        print

    # print
    # print "/* Begin JSON mapping */"
    # print "{"
    # all_mappings.sort(key=lambda t: t[1])
    # for item in all_mappings:
    #     print "\t\"{}\": {},".format(item[0], item[1])
    # print "}"    
    # print "/* End JSON */"

