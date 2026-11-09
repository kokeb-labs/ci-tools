// Seeded violation: one path through a value-returning function ends without a return.
#include <cstdint>

namespace kv::rule_9_6_5::bad {

std::int32_t sign(std::int32_t v) {
  if (v > 0) {
    return 1;
  }
  if (v < 0) {  // seeded: codeql
    return -1;
  }
}  // seeded: gcc,clang

}  // namespace kv::rule_9_6_5::bad
