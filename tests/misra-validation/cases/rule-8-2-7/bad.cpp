// Seeded violation: a pointer is cast to an integer.
#include <cstdint>

namespace kv::rule_8_2_7::bad {

std::uintptr_t address_of(const std::uint32_t* word) {
  return reinterpret_cast<std::uintptr_t>(word);  // seeded
}

}  // namespace kv::rule_8_2_7::bad
