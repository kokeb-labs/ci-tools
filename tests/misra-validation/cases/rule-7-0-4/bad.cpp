// Seeded violation: bitwise and shift operators applied to signed operands.
#include <cstdint>

namespace kv::rule_7_0_4::bad {

std::int32_t low_nibble(std::int32_t v) { return v & 0x0F; }

std::int32_t shifted(std::int32_t v) { return v << 2; }

}  // namespace kv::rule_7_0_4::bad
