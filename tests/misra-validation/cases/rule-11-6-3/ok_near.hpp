// Near misses (near): all-implicit values, and an explicit alias.
#ifndef KV_RULE_11_6_3_OK_NEAR_HPP
#define KV_RULE_11_6_3_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_11_6_3::ok_near {

enum class Step : std::uint8_t { kOne, kTwo, kThree };

enum class Reg : std::uint8_t { kCtrl = 1, kControl = 1, kStat = 2 };

inline bool first(Step s, Reg r) { return (s == Step::kOne) && (r == Reg::kCtrl); }

}  // namespace kv::rule_11_6_3::ok_near

#endif  // KV_RULE_11_6_3_OK_NEAR_HPP
