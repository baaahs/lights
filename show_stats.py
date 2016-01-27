import pstats

p = pstats.Stats("Stats")

p.sort_stats("time")
p.print_stats(100)
