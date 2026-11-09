// Seeded violation: one object modified, or read and modified, without sequencing.
#include <cstdint>

namespace kv::rule_4_6_1::bad {

std::uint32_t combine(std::uint32_t a, std::uint32_t b) { return a ^ b; }

std::uint32_t two_writes(std::uint32_t i) {
  return i++ + i++;  // seeded
}

std::uint32_t both(std::uint32_t i) {
  return combine(i++, i++);  // seeded
}

std::uint32_t read_write(std::uint32_t i) {
  return i + i++;  // seeded
}

}  // namespace kv::rule_4_6_1::bad
