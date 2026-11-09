// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_7_0_5::bad_edge {

std::uint32_t area(std::uint16_t w, std::uint16_t h) { return w * h; }

std::uint32_t flip(std::uint8_t v) { return ~v; }

std::uint32_t scaled(std::uint8_t v) { return v << 2U; }

}  // namespace kv::rule_7_0_5::bad_edge
