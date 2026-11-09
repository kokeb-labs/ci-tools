// Seeded violation of the claimed query (from the main case), so the case also proves detection.
#include <cstdint>

namespace kv::rule_4_1_1_has_include::bad {

__attribute__((noinline)) std::uint32_t twice(std::uint32_t v) { return v << 1U; }  // seeded

}  // namespace kv::rule_4_1_1_has_include::bad
