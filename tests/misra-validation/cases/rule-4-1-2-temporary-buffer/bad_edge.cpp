// Edge cases: more forms of the violation.
#include <cstddef>
#include <cstdint>
#include <memory>

namespace kv::rule_4_1_2_temporary_buffer::bad_edge {

template <typename T>
std::ptrdiff_t room() {
  const auto buf = std::get_temporary_buffer<T>(2);
  std::return_temporary_buffer(buf.first);
  return buf.second;
}
std::ptrdiff_t room_bytes() { return room<std::uint8_t>(); }

}  // namespace kv::rule_4_1_2_temporary_buffer::bad_edge
