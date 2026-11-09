// Seeded violations: a pointer made from an integer, and an object pointer made from void*.
#include <cstdint>

namespace kv::rule_8_2_6::bad {

volatile std::uint32_t* status_register() {
  return reinterpret_cast<volatile std::uint32_t*>(0x40000000U);  // seeded
}

std::uint32_t first_word(void* raw) {
  return *static_cast<std::uint32_t*>(raw);  // seeded
}

}  // namespace kv::rule_8_2_6::bad
