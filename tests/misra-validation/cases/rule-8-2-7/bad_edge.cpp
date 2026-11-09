// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_8_2_7::bad_edge {

std::intptr_t signed_address(std::uint32_t const* p) { return reinterpret_cast<std::intptr_t>(p); }

std::uintptr_t c_style(std::uint32_t const* p) { return (std::uintptr_t)p; }

}  // namespace kv::rule_8_2_7::bad_edge
