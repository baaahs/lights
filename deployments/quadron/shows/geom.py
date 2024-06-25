import math

# Some basic facts about the Quadron
SHORT_SIDE = 36
LONG_SIDE = 60


# The keys are all cell_ids. The values are the xyz position for
# that cell_id in space. This gets populated as edges are told to
# build their XYZ values
cells_in_space = {}

def distance_to(start, end):
    """
    Takes two xyz tuples and returns the distance between them
    """
    p0 = math.pow(start[0] - end[0], 2)
    p1 = math.pow(start[1] - end[1], 2)
    p2 = math.pow(start[2] - end[2], 2)

    return math.sqrt(p0 + p1 + p2)


class Edge(object):
    def __init__(self, channel, sheep_num, sheep_side, pixels_forward, consolidate_reversed, is_long=False):
        self.channel = channel
        self.pixels_forward = pixels_forward
        self.consolidate_reversed = consolidate_reversed
        self.is_long = is_long
        self.xyz = {}
        self.distances = {}

        # Make the fade candy total universe pixel offsets
        start = channel * 64
        self.num_pixels = SHORT_SIDE
        if is_long:
            self.num_pixels = LONG_SIDE

        end = start + self.num_pixels
        step = 1

        if not pixels_forward:
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

    def create_xyz(self, start, end):
        """
        Create the xyz array which maps every led to xyz space. This edge
        will begin at the start coordinate and will increment by the offset
        for each led
        """
        self.xyz = {}
        cursor = start
        offset = ( (end[0] - start[0]) / self.num_pixels, 
            (end[1] - start[1]) / self.num_pixels, 
            (end[2] - start[2]) / self.num_pixels )

        for ix in range(0, self.num_pixels):
            cell_id = self.cell_ids[ix]
            self.xyz[cell_id] = cursor
            cells_in_space[cell_id] = cursor

            cursor = (cursor[0] + offset[0], cursor[1] + offset[1], cursor[2] + offset[2])

    def calculate_neighbor_distances(self, edges):
        """
        Given an dictionary of all edges including presumably myself, calculate
        a distance from each led in this edge to every other led
        """

        # Key this on cell_ids which are unique (panel nums are not)
        self.distances = {}
        for key in edges:
            other = edges[key]
            for ix in range(0, self.num_pixels):
                cell_id = self.cell_ids[ix]

                if cell_id in self.distances:
                    cell_to_other = self.distances[cell_id]
                else:
                    cell_to_other = {}
                    self.distances[cell_id] = cell_to_other

                if not cell_id in self.xyz:
                    continue

                for other_ix in range(0, other.num_pixels):
                    other_cell_id = other.cell_ids[other_ix]
                    if other_cell_id == cell_id:
                        # Ignore myself
                        continue

                    if other_cell_id in other.xyz:
                        cell_to_other[other_cell_id] = distance_to(self.xyz[cell_id], other.xyz[other_cell_id]) 

    def cells_that_neighbor(self, cell_id, distance):
        """
        Returns a list of cells that neighbor the given cell_id within
        the specified distance.
        """
        if not cell_id in self.distances:
            return []

        to_others = self.distances[cell_id]
        out = []
        for other_id, d in to_others.items():
            if d < distance:
                out.append(other_id)

        return out                   


class CompositeEdge(object):
    def __init__(self, edges):
        self.edges = edges
        self.consolidate_reversed = False
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
            if edge.consolidate_reversed:
                self.pixels += reversed(edge.pixels)
                self.panel_nums += reversed(edge.panel_nums)
                self.cell_ids += reversed(edge.cell_ids)
            else:
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
# If the panel numbers or pixel numbers change a new mapping must be generated
base_edges = {
    "BOTTOM_REAR_LEFT":   Edge( 0, 1, "p", False,  False),        # Rev
    "BOTTOM_FRONT_LEFT":  Edge( 1, 2, "p",  True,  False),        # Forward
    "BOTTOM_LEFT_LS":     Edge( 2, 3, "p",  True,  False, True),  # Forward

    "BOTTOM_FRONT_RIGHT": Edge( 3, 2, "b",  True,  True),        # rev
    "BOTTOM_REAR_RIGHT":  Edge(12, 1, "b", False, True),        # Forward
    "BOTTOM_RIGHT_LS":    Edge( 5, 3, "b", False, True, True),  # Forward

    "TOP_REAR_LEFT":      Edge( 6, 4, "p", False, True),        # Rev
    "TOP_REAR_MIDDLE":    Edge( 7, 5, "p", False, True),        # Rev
    "TOP_REAR_RIGHT":     Edge( 8, 6, "p",  True, True),        # Forward

    "TOP_FRONT_RIGHT":    Edge(10, 6, "b",  True, False),        # Rev
    "TOP_FRONT_MIDDLE":   Edge(11, 5, "b",  True, False),        # Rev
    "TOP_FRONT_LEFT":     Edge( 9, 4, "b", False, False),        # Forward
}
edges = base_edges.copy()


# Points that the sides are defined between
PT_A = ( 0.0,   0.0, 0.0)
PT_B = ( 0.615, 1.0, 0.367)
PT_C = (-0.615, 1.0, 0.367)
PT_D = ( 0.0,   2.0, 0.0)

def o(base, off):
    return list(map(sum, list(zip(base, off))))

# EDGE_AC = (PT_C[0] - PT_A[0], PT_C[1] - PT_A[1], PT_C[2] - PT_A[2])
# EDGE_AB = (PT_B[0] - PT_A[0], PT_B[1] - PT_A[1], PT_B[2] - PT_A[2])
# EDGE_CD = (PT_D[0] - PT_C[0], PT_D[1] - PT_C[1], PT_D[2] - PT_C[2])
# EDGE_BD = (PT_D[0] - PT_B[0], PT_D[1] - PT_B[1], PT_D[2] - PT_B[2])
# EDGE_AD = (PT_D[0] - PT_A[0], PT_D[1] - PT_A[1], PT_D[2] - PT_A[2])
# EDGE_CB = (PT_B[0] - PT_C[0], PT_B[1] - PT_C[1], PT_B[2] - PT_C[2])

base_edges["BOTTOM_REAR_LEFT"].create_xyz( o(PT_A, (-.02, 0, 0)), o(PT_C, (-.02, 0, 0)) )
base_edges["BOTTOM_FRONT_LEFT"].create_xyz( o(PT_C, (-.02, 0, 0)), o(PT_D, (-.02, 0, 0)) )
base_edges["BOTTOM_LEFT_LS"].create_xyz( o(PT_D, (-.02, .02, 0)), o(PT_A, (-.02, -0.02, 0)) )

base_edges["BOTTOM_FRONT_RIGHT"].create_xyz( o(PT_B, (.02, 0, 0)), o(PT_D, (.02, 0, 0)) )
base_edges["BOTTOM_REAR_RIGHT"].create_xyz( o(PT_A, (.02, 0, 0)), o(PT_B, (.02, 0, 0)) )
base_edges["BOTTOM_RIGHT_LS"].create_xyz( o(PT_D, (.02, .05, 0)), o(PT_A, (.02, 0.01, 0)) )

base_edges["TOP_REAR_LEFT"].create_xyz( PT_A, PT_C )
base_edges["TOP_REAR_MIDDLE"].create_xyz( PT_C, PT_B )
base_edges["TOP_REAR_RIGHT"].create_xyz( PT_B, PT_A )

base_edges["TOP_FRONT_RIGHT"].create_xyz( PT_B, PT_D )
base_edges["TOP_FRONT_MIDDLE"].create_xyz( PT_C, PT_B )
base_edges["TOP_FRONT_LEFT"].create_xyz( PT_D, PT_C )

for name in base_edges:
    edge = base_edges[name]
    edge.calculate_neighbor_distances(base_edges)








# Now add the Composite edges
faces = {
    "BOTTOM_LEFT_ALL": CompositeEdge.using("BOTTOM_REAR_LEFT", "BOTTOM_FRONT_LEFT", "BOTTOM_LEFT_LS"),
    "BOTTOM_RIGHT_ALL": CompositeEdge.using("BOTTOM_FRONT_RIGHT", "BOTTOM_REAR_RIGHT", "BOTTOM_RIGHT_LS"),
    "TOP_REAR_ALL": CompositeEdge.using("TOP_REAR_LEFT", "TOP_REAR_RIGHT", "TOP_REAR_MIDDLE",),
    "TOP_FRONT_ALL": CompositeEdge.using("TOP_FRONT_RIGHT", "TOP_FRONT_LEFT", "TOP_FRONT_MIDDLE"),
}
edges.update(faces)

all_edges = CompositeEdge(list(base_edges.values()))

party = CompositeEdge.using("BOTTOM_LEFT_ALL","TOP_REAR_ALL")
business = CompositeEdge.using("BOTTOM_RIGHT_ALL", "TOP_FRONT_ALL")

##############
# Historically animations looked for "panel numbers" which are shared between
# party and business side. The sheep_side objects then append a side indicator
# to those numbers.

ALL = party.panel_nums

# Some interesting slices
by_edges = [edge.cell_ids for edge in list(base_edges.values())]
by_faces = [edge.cell_ids for edge in list(faces.values())]

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
    for name, edge in base_edges.items():
        print("[{}]".format(name))

        if "1p" in edge.distances:
            print(edge.distances["1p"])
        # print edge.distances
        lst = edge.mapping_list()
        # print lst
        all_mappings += lst
        # print

    print()
    print("/* Begin JSON mapping */")
    print("{")
    all_mappings.sort(key=lambda t: t[1])
    for item in all_mappings:
        print("\t\"{}\": {},".format(item[0], item[1]))
    print("}")    
    print("/* End JSON */")

