// Seeded violation: one object modified twice without sequencing.
#include <cstdint>

namespace kv::rule_4_6_1::bad {

std::uint32_t combine(std::uint32_t a, std::uint32_t b) { return a ^ b; }

std::uint32_t bump(std::uint32_t i) {
  i = i++ + 1U;  // two unsequenced writes to i
  return i;
}

std::uint32_t both(std::uint32_t i) {
  return combine(i++, i++);  // two unsequenced writes in one call
}

std::uint32_t read_write(std::uint32_t i) {
  return i + i++;  // a read and a write without ordering
}

}  // namespace kv::rule_4_6_1::bad
