// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_6_0_1::bad_edge {

struct Counter {
  std::int32_t start{0};
};
std::int32_t vexing() {
  Counter c(Counter());  // declares a function c taking a function returning Counter
  void reset();          // a block-scope declaration of a free function
  return 1;
}

}  // namespace kv::rule_6_0_1::bad_edge
