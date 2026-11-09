// Seeded violation: a value stored into a local and overwritten before any read.
#include <cstdint>

namespace kv::rule_0_1_1::bad {

std::uint32_t pick(std::uint32_t a) {
  std::uint32_t r = a;  // seeded
  r = 7U;  // the value written above is never read
  return r;
}

}  // namespace kv::rule_0_1_1::bad
