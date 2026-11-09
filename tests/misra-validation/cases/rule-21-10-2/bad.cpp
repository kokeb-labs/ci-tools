// Seeded violation: a non-local jump with setjmp and longjmp.
#include <csetjmp>

namespace kv::rule_21_10_2::bad {

int jump_back() {
  std::jmp_buf context;
  if (setjmp(context) != 0) {
    return 1;
  }
  std::longjmp(context, 1);
}

}  // namespace kv::rule_21_10_2::bad
