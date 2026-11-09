// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_20_1_OK_NEAR_HPP
#define KV_RULE_8_20_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_8_20_1::ok_near {

inline std::uint32_t top_less_one() { return 0xFFFFFFFFU - 1U; }

inline std::uint64_t wide_sum() { return 0xFFFFFFFFULL + 0xFFFFFFFFULL; }

}  // namespace kv::rule_8_20_1::ok_near

#endif  // KV_RULE_8_20_1_OK_NEAR_HPP
