;; 1 loops found
;;
;; Loop 0
;;  header 0, latch 1
;;  depth 0, outer -1
;;  nodes: 0 1 2 3 4
;; 2 succs { 3 4 }
;; 3 succs { 4 }
;; 4 succs { 1 }
void case13_main() ()
<bb 2>:
  lock ();
  g1_case13.1 = g1_case13;
  retval.0 = g1_case13.1 == 0;
  if (retval.0 != 0)
    goto
<bb 3>:
  unlock ();
<bb 4>:
  g1_case13 = 255;
  return;

}