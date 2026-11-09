// Seeded violation: setjmp and longjmp through <setjmp.h>, the jump buffer a static object.
#include <setjmp.h>

namespace kv::rule_21_10_2::bad_c_header {

static jmp_buf recovery;

void fail() { longjmp(recovery, 2); }  // seeded

int guarded() {
  if (setjmp(recovery) != 0) {  // seeded
    return 1;
  }
  fail();
  return 0;
}

}  // namespace kv::rule_21_10_2::bad_c_header
