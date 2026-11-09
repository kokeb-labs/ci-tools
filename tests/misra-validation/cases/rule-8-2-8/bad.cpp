// Seeded violation: a pointer is cast to an integer type other than std::uintptr_t or std::intptr_t.
#include <cstdint>

namespace kv::rule_8_2_8::bad {

std::uint64_t address_of(const std::uint32_t* word) {
  return reinterpret_cast<std::uint64_t>(word);  // seeded
}

}  // namespace kv::rule_8_2_8::bad
