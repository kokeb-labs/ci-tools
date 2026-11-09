// Seeded violation: the deprecated temporary buffer functions.
#include <memory>
#include <cstdint>

namespace kv::rule_4_1_2_temporary_buffer::bad {

std::ptrdiff_t scratch() {
  const auto buf = std::get_temporary_buffer<std::uint32_t>(4);  // seeded
  std::return_temporary_buffer(buf.first);  // seeded
  return buf.second;
}

}  // namespace kv::rule_4_1_2_temporary_buffer::bad
