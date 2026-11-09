// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_7_11_3::bad_edge {

std::int32_t two() { return 2; }

using Fn = std::int32_t (*)();

std::int32_t call(Fn f) { return f(); }

std::int32_t by_name() { return call(two); }

bool exists() {
  if (two) {
    return true;
  }
  return false;
}

}  // namespace kv::rule_7_11_3::bad_edge
