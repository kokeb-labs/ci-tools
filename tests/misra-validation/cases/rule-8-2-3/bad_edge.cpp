// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_8_2_3::bad_edge {

void clear(std::uint32_t* const* table) {
  std::uint32_t** writable = const_cast<std::uint32_t**>(table);
  **writable = 0U;
}

void zero(std::uint32_t const& value) {
  std::uint32_t& writable = const_cast<std::uint32_t&>(value);
  writable = 0U;
}

}  // namespace kv::rule_8_2_3::bad_edge
