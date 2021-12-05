(import [numpy :as np])
(import random)
(import math)

(setv GRID_SIZE 5)
(setv EMPTY_CELL 0)
(setv PLAYER 1)
(setv ALIEN 2)
(setv ASTEROID 3)
(setv PLAYER_LASER 4)
(setv ALIEN_LASER 5)
(setv DEPTH 3)

(setv START_PLAYER_POSITION [4 2])
(setv START_ALIEN_POSITION [0 2])
(setv CURRENT_PLAYER_POS [None])
(setv MOVE_LEFT [0 -1])
(setv MOVE_RIGHT [0 1])
(setv MOVE_DOWN [1 0])
(setv MOVE_UP [-1 0])




(defn copy_grid [grid]
    (return
        (lfor i (range GRID_SIZE)
        (lfor j (range GRID_SIZE)
        (get (get grid i) j)))
    )
)

(defn set_grid_value [grid pos value]
    (setv x (get pos 0))
    (setv y (get pos 1))
    (assoc (get grid x) y value)
)

(defn get_grid_value [grid pos]
    (setv x (get pos 0))
    (setv y (get pos 1))
    (return (get (get grid x) y))
)

(defn pos_out_of_bound [pos]
    (setv x (get pos 0))
    (setv y (get pos 1))

    (return
        (not
            (and
                (and (>= y 0) (<= y 4))
                (and (>= x 0) (<= x 4))
            )
        )
    )
)

(defn generate_grid []
    (setv grid (lfor i (range 5) (lfor j (range 5) EMPTY_CELL)))
    (for [x (range GRID_SIZE)]
        (for [y (range GRID_SIZE)]
            (setv v
                (cond
                    [(and (= y (get START_PLAYER_POSITION 0)) (= x (get START_PLAYER_POSITION 1))) PLAYER]
                    [(and (= y (get START_ALIEN_POSITION 0)) (= x (get START_ALIEN_POSITION 1))) ALIEN]
                    [(and (> (random.uniform 0 1) 0.75) (< y 4) (> y 0)) ASTEROID]
                )
            )
            (if (= None v) (continue))
            (set_grid_value grid [y x] v)
        )
    )

    (return grid)
)

(defn get_current_pos [maze who]
    (setv pos (np.where (= (np.array maze) who)))
    (if (= (len (get pos 0)) 0)
        (return)
    )
    (return [(get (get pos 0) 0) (get (get pos 1) 0)])
)

(defn add_pos_lists [pos delta]
    (return
        [
            (+ (get pos 0) (get delta 0))
            (+ (get pos 1) (get delta 1))
        ]
    )
)

(defn get_available_moves [gri who]
    (setv curr_pos (get_current_pos gri who))
    (setv moves [])
    (do
        (setv x (get curr_pos 0))
        (setv y (get curr_pos 1))
        (if (and (!= 0 y) (!= 3 (get (get gri x) (- y 1))))
            (doto moves (.append (add_pos_lists curr_pos MOVE_LEFT))))
        (if (and (!= 4 y) (!= 3 (get (get gri x) (+ y 1))))
            (doto moves (.append (add_pos_lists curr_pos MOVE_RIGHT))))
    )
    (if (= who ALIEN)
        (do

            (if (and (!= 3 (get (get gri (+ x 1)) y)) (or (= y 0) (= y 4)))
                (doto moves (.append (add_pos_lists curr_pos MOVE_DOWN))))
        )
    )

    (return moves)
)




(defn move_grid_member [gri who pos]
    (setv curr_pos (get_current_pos gri who))
    (set_grid_value gri curr_pos 0)
    (set_grid_value gri pos who)
    (return gri)
)

(defn update_laser [grid laser]
    (setv curr_pos_laser (get_current_pos grid laser))
    (setv clean_previous True)
    (setv side (if (= laser PLAYER_LASER) PLAYER ALIEN))
    (setv curr_pos_side (get_current_pos grid side))

    (if (is curr_pos_laser None)
        (do

            (setv curr_pos_laser curr_pos_side)
            (setv clean_previous False)
        )
    )

    (if (= side PLAYER)
        (do
            (setv next_cell_pos [(- (get curr_pos_side 0) 1) (get curr_pos_side 1)])
            (if (pos_out_of_bound next_cell_pos) (return))
            (setv next_cell_val (get_grid_value grid next_cell_pos))
        )
        (do
            (setv next_cell_pos [(+ (get curr_pos_side 0) 1) (get curr_pos_side 1)])
            (if (pos_out_of_bound next_cell_pos) (return))
            (setv next_cell_val (get_grid_value grid next_cell_pos))
        )
    )
    (if (!= next_cell_val EMPTY_CELL)
        (set_grid_value grid next_cell_pos EMPTY_CELL)
        (set_grid_value grid next_cell_pos laser)
    )
    (if clean_previous (set_grid_value grid curr_pos_laser EMPTY_CELL))
    (return grid)
)

(defn euclidean [x1 x2 y1 y2]
    (return (** (+ (** (- x1 x2) 2) (** (- y1 y2) 2)) 0.5))
)

(defclass Node []

    (defn __init__ [self grid]

        (setv self.grid grid)

        (setv self.children [])
        (setv self.score 0)
        (setv self.move None)
        (setv self.level DEPTH)

    )

    (defn get_children [self max_player depth]
        (setv children [])
        (setv player_or_alien (if max_player PLAYER ALIEN))
        (setv laser_type (if max_player PLAYER_LASER ALIEN_LASER))

        (for [move (get_available_moves self.grid player_or_alien)]
            (do


                (setv grid_cp (copy_grid self.grid))

                (setv grid_cp (move_grid_member grid_cp player_or_alien move))

                (setv grid_cp (update_laser grid_cp laser_type))


                (setv node_tmp (Node grid_cp))
                (setv node_tmp.move move)
                (setv node_tmp.level depth)
                (doto children (.append node_tmp))
            )
        )
        (setv self.children children)
        (return children)
    )

    (defn evaluate [self]
        (setv player_pos (get_current_pos self.grid PLAYER))
        (if (is player_pos None) (return -10000))
        (setv alien_pos (get_current_pos self.grid ALIEN))
        (if (is alien_pos None) (return 10000))
        (setv x1 (get player_pos 0))
        (setv y1 (get player_pos 1))
        (setv x2 (get alien_pos 0))
        (setv y2 (get alien_pos 1))
        (setv res (/ 1 (euclidean x1 x2 y1 y2)))
        (setv alien_laser_pos (get_current_pos self.grid ALIEN_LASER))

        (if (!= alien_laser_pos None)
            (do
                (setv x3 (get alien_laser_pos 0))
                (setv y3 (get alien_laser_pos 1))
                (setv res (+ res (euclidean x1 x3 y1 y3)))
            )
        )
        (return res)
    )

    (defn game_over [self]
        (return
            (or
                (is (get_current_pos self.grid PLAYER) None)
                (is (get_current_pos self.grid ALIEN) None)
            )
        )
    )

    (defn __str__ [self]

        (setv ret (+ (* "\t" (* -1 (- self.level DEPTH))) (str self.move) "->" (str self.score) "\n"))

        (for [child self.children]

            (setv ret (+ ret (child.__str__)))

        )
        (return ret)
    )
)


(defn minimax [node depth max_player]
    (if (or (= depth 0) (node.game_over))
        (do
            (setv score (node.evaluate))
            (setv node.score score)
            (return score)
        )
    )
    (if max_player
        (do
            (setv max_eval -Inf)
            (for [child_node (node.get_children max_player (- depth 1))]
                (do
                    (setv score (minimax child_node (- depth 1) False))
                    (setv max_eval (max max_eval score))
                )
            )
            (setv node.score max_eval)
            (return max_eval)
        )

        (do
            (setv min_eval Inf)
            (for [child_node (node.get_children max_player (- depth 1))]
                (do
                    (setv score (minimax child_node (- depth 1) True))
                    (setv min_eval (min min_eval score))
                )
            )
            (setv node.score min_eval)
            (return min_eval)
        )
    )
)


(setv grid (generate_grid))

(print (np.array grid))
(setv node (Node grid))
(minimax node DEPTH True)
(print node)