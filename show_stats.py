import pstats

p = pstats.Stats("Stats")

p.sort_stats("cumulative")
p.print_stats(100)
