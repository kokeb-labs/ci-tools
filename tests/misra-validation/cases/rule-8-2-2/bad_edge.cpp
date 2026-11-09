// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_8_2_2::bad_edge {

using Word = std::uint16_t;

Word low(std::uint32_t v) { return Word(v); }  // seeded

std::uint32_t const* view(void const* raw) { return (std::uint32_t const*)raw; }  // seeded

template <typename T>
T convert(std::int64_t v) {
  return T(v);  // seeded
}

std::int32_t use(std::int64_t v) { return convert<std::int32_t>(v); }

}  // namespace kv::rule_8_2_2::bad_edge
