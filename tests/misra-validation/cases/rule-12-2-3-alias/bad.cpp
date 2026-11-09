// Seeded violation: a named one-bit bit-field of a signed fixed-width alias.
#include <cstdint>

namespace kv::rule_12_2_3_alias::bad {

struct Bits {
  std::int8_t enabled : 1;  // seeded
};

bool on(const Bits& b) { return b.enabled != 0; }

}  // namespace kv::rule_12_2_3_alias::bad
