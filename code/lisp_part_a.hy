(import [pandas :as pd])
(import [numpy :as np])
(import math)
(import os)

(setv csv_file_path (os.path.join (os.path.dirname (os.path.abspath __file__)) ".." "results.csv"))

(print csv_file_path)
(setv dataset (pd.read_csv csv_file_path))

(setv time_series (get dataset "time"))
(setv score_series (get dataset "score"))

(defn calc_mean[ser]
    (/ (ser.sum) (len ser))
)

(defn calc_variance [ser]
    (return (/ (sum (** (- ser (calc_mean ser)) 2)) (len ser)))
)

(print "Mean:" (calc_mean time_series))
(print "Variance:" (calc_variance score_series))
