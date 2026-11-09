// Compliant: a fixed parameter list, no ellipsis at all.
#ifndef KV_RULE_8_2_11_OK_HPP
#define KV_RULE_8_2_11_OK_HPP

#include <cstdint>

namespace kv::rule_8_2_11::ok {

struct Sample {
  std::int32_t value{0};
};

inline std::int32_t first(const Sample& s) { return s.value; }

}  // namespace kv::rule_8_2_11::ok

#endif  // KV_RULE_8_2_11_OK_HPP
