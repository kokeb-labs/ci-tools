// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_8_2_3::bad_edge {

void zero(std::uint32_t const& value) {
  std::uint32_t& writable = const_cast<std::uint32_t&>(value);  // seeded: clang-tidy
  writable = 0U;
}

}  // namespace kv::rule_8_2_3::bad_edge
