// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_6_2_3_TYPE_OK_NEAR_HPP
#define KV_RULE_6_2_3_TYPE_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_6_2_3_type::near {

// One class definition in one header, used by two translation units.
struct Frame {
  std::int32_t raw{0};
};
inline std::int32_t raw_of(const Frame& f) { return f.raw; }
std::int32_t raw_twice(const Frame& f);

}  // namespace kv::rule_6_2_3_type::near

#endif  // KV_RULE_6_2_3_TYPE_OK_NEAR_HPP
