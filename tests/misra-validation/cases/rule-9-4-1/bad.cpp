// Seeded violation: an if / else-if chain with no final else.
#include <cstdint>

namespace kv::rule_9_4_1::bad {

std::int32_t classify(std::int32_t v) {
  std::int32_t c = 0;
  if (v < 0) {  // seeded: codeql
    c = -1;
  } else if (v > 0) {  // seeded: clang-tidy
    c = 1;
  }
  return c;
}

}  // namespace kv::rule_9_4_1::bad
