;; 1 loops found
;;
;; Loop 0
;;  header 0, latch 1
;;  depth 0, outer -1
;;  nodes: 0 1 2
;; 2 succs { 1 }
void svp_simple_013_001_isr_1() ()
<bb 2>:
  idlerun ();
  svp_simple_013_001_global_var1 = 1;
  idlerun ();
  return;

}