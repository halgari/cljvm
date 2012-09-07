((fn rec (cur max) 
	(if (= cur max) 
	    cur
	    (rec (baz 1 cur) max)))
0 10000000)
