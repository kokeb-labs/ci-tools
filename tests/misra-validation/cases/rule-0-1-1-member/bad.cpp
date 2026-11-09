// Seeded violation of the claimed query (from the main case), so the case also proves detection.
#include <cstdint>

namespace kv::rule_0_1_1_member::bad {

std::uint32_t pick(std::uint32_t a) {
  std::uint32_t r = a;  // seeded
  r = 7U;  // the value written above is never read
  return r;
}

}  // namespace kv::rule_0_1_1_member::bad
