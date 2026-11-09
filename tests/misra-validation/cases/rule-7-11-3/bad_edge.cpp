// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_7_11_3::bad_edge {

std::int32_t two() { return 2; }

using Fn = std::int32_t (*)();

Fn decayed() { return +two; }  // seeded

bool exists() {
  if (two) {  // seeded
    return true;
  }
  return false;
}

}  // namespace kv::rule_7_11_3::bad_edge
