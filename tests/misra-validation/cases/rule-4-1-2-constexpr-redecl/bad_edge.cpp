// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_4_1_2_constexpr_redecl::bad_edge {

struct Range {
  static constexpr std::uint32_t kLow = 1U;
  static constexpr std::uint32_t kHigh = 9U;
};
constexpr std::uint32_t Range::kLow;  // seeded
constexpr std::uint32_t Range::kHigh;  // seeded
std::uint32_t span() { return Range::kHigh ^ Range::kLow; }

}  // namespace kv::rule_4_1_2_constexpr_redecl::bad_edge
