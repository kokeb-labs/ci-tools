// Seeded violation (local): a volatile local with no hardware behind it.
#include <cstdint>

namespace kv::rule_10_1_2::bad_local {

std::int32_t count(std::int32_t n) {
  volatile std::int32_t c = 0;  // seeded
  for (std::int32_t i = 0; i < n; ++i) {
    c = c + 1;
  }
  return c;
}

}  // namespace kv::rule_10_1_2::bad_local
