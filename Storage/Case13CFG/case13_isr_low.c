;; 1 loops found
;;
;; Loop 0
;;  header 0, latch 1
;;  depth 0, outer -1
;;  nodes: 0 1 2
;; 2 succs { 1 }
void case13_isr_low() ()
<bb 2>:
  lock ();
  idlerun ();
  unlock ();
  return;

}