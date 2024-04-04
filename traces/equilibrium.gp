
    # set term pngcairo transparent truecolor
    set term svg
    set output "img/equilibrium.svg"

    set datafile separator ","

    set timefmt '%S'
    set format x ""
    set xdata time

    set key noautotitle
    set xlabel 'Time'

    set style line 101 lw 2 lt rgb "#ba0306"
    set style line 102 lw 2 lt rgb "#aaaaaa"
    set style line 103 lw 2 lt rgb "#2e2e2e"

    set style line 11 lc rgb '#808080' lt 1
    set border 3 back ls 11
    set tics nomirror

    set multiplot layout 3,1 rowsfirst

    set title "Input"
    set ylabel "Flow Rate"
    set ytics scale 0.5 10
    plot "traces/equilibrium.csv" using 1:3 with lines ls 102

    set title "System State"
    set ylabel "Temperature"
    set ytics scale 0.5 1
    plot "traces/equilibrium.csv" using 1:2 with lines ls 101

    set title "Control"
    set ylabel "Flow Rate"
    set ytics scale 0.5 20
    plot "traces/equilibrium.csv" using 1:4 with lines ls 103

    unset multiplot
    