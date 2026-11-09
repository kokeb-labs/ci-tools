#ifndef KV_RULE_6_2_3_TYPE_OK_HPP
#define KV_RULE_6_2_3_TYPE_OK_HPP

// Compliant: the type is defined once, in a header.
#include <cstdint>

namespace kv::rule_6_2_3_type::ok {

struct Sample {
  std::int32_t raw{0};
};

inline std::int32_t raw_of(Sample const& s) { return s.raw; }

}  // namespace kv::rule_6_2_3_type::ok

#endif  // KV_RULE_6_2_3_TYPE_OK_HPP
