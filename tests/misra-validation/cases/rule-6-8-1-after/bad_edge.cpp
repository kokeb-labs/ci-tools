// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_6_8_1_after::bad_edge {

std::int32_t last_seen(std::int32_t n) {
  const std::int32_t* p = nullptr;
  for (std::int32_t i = 0; i < n; ++i) {
    const std::int32_t copy = i;
    p = &copy;
  }
  return (p != nullptr) ? *p : 0;  // the loop body's local is gone
}

}  // namespace kv::rule_6_8_1_after::bad_edge
