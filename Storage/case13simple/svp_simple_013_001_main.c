void svp_simple_013_001_main() ()
;; 1 loops found
;;
;; Loop 0
;;  header 0, latch 1
;;  depth 0, outer -1
;;  nodes: 0 1 2
;; 2 succs { 1 }
void svp_simple_013_001_main() ()
<bb 2>:
  init ();
  disable_isr (1);
  reader1 = svp_simple_013_001_global_var1;
  return;

}