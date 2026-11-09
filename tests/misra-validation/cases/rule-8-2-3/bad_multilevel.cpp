// Seeded violation (multilevel): const_cast removes const below the first pointer level.
#include <cstdint>

namespace kv::rule_8_2_3::bad_multilevel {

void clear(std::uint32_t* const* table) {
  std::uint32_t** writable = const_cast<std::uint32_t**>(table);  // seeded
  **writable = 0U;
}

}  // namespace kv::rule_8_2_3::bad_multilevel
