// Seeded violation: unsigned arithmetic on constants that wraps around.
#include <cstdint>

namespace kv::rule_8_20_1::bad {

std::uint32_t wrapped() {
  return 0xFFFFFFFFU + 2U;
}

}  // namespace kv::rule_8_20_1::bad
