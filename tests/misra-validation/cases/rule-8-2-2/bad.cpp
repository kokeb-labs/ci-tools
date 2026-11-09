// Seeded violations: a C-style cast and a functional-notation cast.
#include <cstdint>

namespace kv::rule_8_2_2::bad {

std::int32_t narrow(std::int64_t wide) {
  return (std::int32_t)wide;
}

std::int32_t narrow_again(std::int64_t wide) {
  return std::int32_t(wide);
}

}  // namespace kv::rule_8_2_2::bad
