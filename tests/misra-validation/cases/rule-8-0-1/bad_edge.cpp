// Edge cases of the seeded violation.
#include <cstddef>
#include <cstdint>

namespace kv::rule_8_0_1::bad_edge {

std::uint32_t combine(std::uint32_t a, std::uint32_t b, std::uint32_t c) { return a & b | c; }

std::uint32_t shift_less(std::uint32_t a, std::uint32_t b) { return a << b - 1U; }

std::size_t width_of(std::uint32_t const* p) { return sizeof *p; }

}  // namespace kv::rule_8_0_1::bad_edge
