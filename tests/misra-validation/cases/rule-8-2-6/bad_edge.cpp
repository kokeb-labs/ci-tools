// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_8_2_6::bad_edge {

std::uint32_t volatile* c_style() { return (std::uint32_t volatile*)0x40001000U; }

std::uint32_t const* from_value(std::uintptr_t address) { return reinterpret_cast<std::uint32_t const*>(address); }

template <typename T>
T* typed(void* raw) {
  return static_cast<T*>(raw);
}

std::uint32_t* use(void* raw) { return typed<std::uint32_t>(raw); }

}  // namespace kv::rule_8_2_6::bad_edge
