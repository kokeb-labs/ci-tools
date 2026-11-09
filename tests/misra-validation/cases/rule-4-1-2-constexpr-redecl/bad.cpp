// Seeded violation: a redundant namespace-scope redeclaration of a static constexpr member.
#include <cstdint>

namespace kv::rule_4_1_2_constexpr_redecl::bad {

struct Limits {
  static constexpr std::uint32_t kMax = 10U;
};
constexpr std::uint32_t Limits::kMax;  // redundant out-of-class redeclaration

}  // namespace kv::rule_4_1_2_constexpr_redecl::bad
