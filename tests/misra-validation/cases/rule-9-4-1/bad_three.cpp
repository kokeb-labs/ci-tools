// Seeded violation (three): a three-armed else-if chain without a final else.
#include <cstdint>

namespace kv::rule_9_4_1::bad_three {

std::int32_t band(std::int32_t v) {
  std::int32_t b = 0;
  if (v < 10) {
    b = 1;
  } else if (v < 100) {  // seeded: codeql
    b = 2;
  } else if (v < 1000) {  // seeded: clang-tidy
    b = 3;
  }
  return b;
}

}  // namespace kv::rule_9_4_1::bad_three
