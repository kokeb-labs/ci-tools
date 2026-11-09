// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_5_7_1::bad_edge {

/**
 * A documentation block that opens /* another comment on its second line.
 */
std::uint32_t two() { return 2U; }

}  // namespace kv::rule_5_7_1::bad_edge
