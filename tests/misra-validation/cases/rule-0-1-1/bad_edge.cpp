// Edge case: an initial value replaced before any read.
#include <cstdint>

namespace kv::rule_0_1_1::bad_edge {

std::uint32_t write_then_overwrite(std::uint32_t a) {
  std::uint32_t tmp = a ^ 5U;  // never read  // seeded
  tmp = a;
  return tmp;
}

}  // namespace kv::rule_0_1_1::bad_edge
