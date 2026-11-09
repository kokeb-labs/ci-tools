// Seeded violation: the bytes of a float are reinterpreted through a pointer cast.
#include <cstdint>

namespace kv::rule_8_2_5::bad {

std::uint32_t bits_of(const float& value) {
  return *reinterpret_cast<const std::uint32_t*>(&value);
}

}  // namespace kv::rule_8_2_5::bad
