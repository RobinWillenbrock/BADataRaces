;; 1 loops found
;;
;; Loop 0
;;  header 0, latch 1
;;  depth 0, outer -1
;;  nodes: 0 1 2
;; 2 succs { 1 }
void case10_isr() ()
<bb 2>:
  idlerun ();
  shared1_case10 = 1;
  idlerun ();
  return;

}