// Seeded violation: a mutable namespace-scope variable.
#include <cstdint>

namespace kv::rule_6_7_2::bad {

std::int32_t g_errors = 0;  // seeded

std::int32_t bump() {
  ++g_errors;
  return g_errors;
}

}  // namespace kv::rule_6_7_2::bad
