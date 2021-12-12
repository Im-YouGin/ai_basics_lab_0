(defn print_multiplication_table [min_v max_v]
    (for [i (range min_v (+ max_v 1))]
        (for [j (range min_v (+ max_v 1))]
            (do
                (setv res (.format "{:>2}" (* i j)))
                (print res :end " ")
            )
        )
        (print)
    )
)
(print_multiplication_table 1 9)
