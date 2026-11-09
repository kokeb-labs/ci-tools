// Near misses (near): default arguments only on non-virtual functions.
#ifndef KV_RULE_13_3_2_OK_NEAR_HPP
#define KV_RULE_13_3_2_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_13_3_2::ok_near {

class Scale {
 public:
  std::uint32_t apply(std::uint32_t v, std::uint32_t shift = 1U) const { return v << shift; }
};

inline std::uint32_t twice(const Scale& s, std::uint32_t v) { return s.apply(v); }

}  // namespace kv::rule_13_3_2::ok_near

#endif  // KV_RULE_13_3_2_OK_NEAR_HPP
