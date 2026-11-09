// Seeded violation (nested): an else-if chain nested in a loop body, missing its final else.
#include <cstdint>

namespace kv::rule_9_4_1::bad_nested {

std::int32_t count(std::int32_t n) {
  std::int32_t pos = 0;
  for (std::int32_t i = -n; i < n; ++i) {
    if (i < 0) {  // seeded: codeql
      pos -= 1;
    } else if (i > 0) {  // seeded: clang-tidy
      pos += 1;
    }
  }
  return pos;
}

}  // namespace kv::rule_9_4_1::bad_nested
