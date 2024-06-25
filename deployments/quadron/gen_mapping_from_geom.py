import shows.geom as geom

all_mappings = []
for name, edge in geom.base_edges.items():
    lst = edge.mapping_list()
    all_mappings += lst

print("{")
all_mappings.sort(key=lambda t: t[1])
comma = "  "
for item in all_mappings:
    print("\t{}\"{}\": {}".format(comma,item[0], item[1]))
    comma = ", "
print("}")    
