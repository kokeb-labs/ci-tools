// Seeded violation of the claimed query, so the case also proves detection.
#include <cstdint>

namespace kv::rule_7_0_6_member_access::bad {

std::uint8_t narrow(std::uint8_t v) { return v; }
std::uint32_t widen(std::uint8_t v) {
  const std::uint32_t w = narrow(v);  // seeded
  return w;
}

}  // namespace kv::rule_7_0_6_member_access::bad
