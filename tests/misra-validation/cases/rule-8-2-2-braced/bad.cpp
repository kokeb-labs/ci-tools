// Seeded violation of the claimed query, so the case also proves detection.
#include <cstdint>

namespace kv::rule_8_2_2_braced::bad {

std::uint32_t widen(std::uint16_t v) { return std::uint32_t(v); }  // seeded

}  // namespace kv::rule_8_2_2_braced::bad
