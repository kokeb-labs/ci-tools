// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_8_2_5::bad_edge {

std::uint32_t bits_ref(float const& value) { return reinterpret_cast<std::uint32_t const&>(value); }

template <typename To, typename From>
To const* view_as(From const* p) {
  return reinterpret_cast<To const*>(p);
}

std::uint16_t first_half(std::uint32_t const* word) { return *view_as<std::uint16_t>(word); }

}  // namespace kv::rule_8_2_5::bad_edge
