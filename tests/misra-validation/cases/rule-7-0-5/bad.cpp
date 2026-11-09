// Seeded violation: small unsigned operands are promoted to signed int by the arithmetic.
#include <cstdint>

namespace kv::rule_7_0_5::bad {

std::uint32_t sum(std::uint8_t a, std::uint8_t b) { return a + b; }

bool mixed(std::uint32_t u, std::int32_t s) { return u < s; }

}  // namespace kv::rule_7_0_5::bad
