// Seeded violation of the claimed query, so the case also proves detection.
#include <cstdint>

namespace kv::rule_7_0_6_implicit_this::bad {

std::uint32_t take(std::uint32_t v) { return v; }
std::uint32_t call() { return take(0); }  // seeded

}  // namespace kv::rule_7_0_6_implicit_this::bad
