// Seeded violation: the deprecated not1 negator.
#include <functional>
#include <cstdint>

namespace kv::rule_4_1_2_negate_adaptor::bad {

struct IsZero {
  using argument_type = std::uint32_t;
  bool operator()(std::uint32_t v) const { return v == 0U; }
};

bool nonzero(std::uint32_t v) {
  std::unary_negate<IsZero> not_zero = std::not1(IsZero{});
  return not_zero(v);
}

}  // namespace kv::rule_4_1_2_negate_adaptor::bad
