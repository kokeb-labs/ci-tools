#ifndef KV_RULE_6_2_4_BAD_HPP
#define KV_RULE_6_2_4_BAD_HPP

// Seeded violation: a header defines non-inline functions with external linkage.
#include <cstdint>

namespace kv::rule_6_2_4::bad {

std::int32_t twice(std::int32_t v) { return v * 2; }  // seeded

struct Scaler {
  std::int32_t apply(std::int32_t v) const;
};
std::int32_t Scaler::apply(std::int32_t v) const { return v * 3; }  // seeded

}  // namespace kv::rule_6_2_4::bad

#endif  // KV_RULE_6_2_4_BAD_HPP
